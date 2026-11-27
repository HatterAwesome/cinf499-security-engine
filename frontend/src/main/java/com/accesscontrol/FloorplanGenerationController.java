package com.accesscontrol;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import javax.imageio.ImageReader;
import javax.imageio.stream.ImageInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.io.IOException;
import java.util.Comparator;
import java.util.Iterator;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

@RestController
@RequestMapping("/api/floorplans")
public class FloorplanGenerationController {

    private final Path projectRoot;
    private final Path pythonExecutable;
    private final long timeoutSeconds;

    private static final long MAX_FILE_SIZE = 5L * 1024 * 1024;
    private static final long MAX_PIXELS = 4_000_000L;

    // Limit concurrent model executions.
    private final Semaphore generationLock = new Semaphore(1);

    public FloorplanGenerationController(
            @Value("${app.floorplan.project-root}") String projectRoot,
            @Value("${app.floorplan.python}") String pythonExecutable,
            @Value("${app.floorplan.timeout-seconds}") long timeoutSeconds) {

        this.projectRoot = Path.of(projectRoot)
                .toAbsolutePath().normalize();

        this.pythonExecutable = Path.of(pythonExecutable)
                .toAbsolutePath().normalize();

        this.timeoutSeconds = timeoutSeconds;
    }

    @PostMapping(
            value = "/generate",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public ResponseEntity<?> generateFloorplan(
            @RequestParam("file") MultipartFile file) {

        if (file.isEmpty() || file.getSize() > MAX_FILE_SIZE) {
            return error(HttpStatus.BAD_REQUEST,
                    "Select an image no larger than 5 MB.");
        }

        if (!generationLock.tryAcquire()) {
            return error(HttpStatus.TOO_MANY_REQUESTS,
                    "Another floor plan is being processed. Please try again.");
        }

        Path temporaryDirectory = null;
        Process process = null;

        try {
            temporaryDirectory =
                    Files.createTempDirectory("floorplan-");

            Path input = temporaryDirectory.resolve("input.img");
            Path output = temporaryDirectory.resolve("generated.png");
            Path log = temporaryDirectory.resolve("generation.log");

            file.transferTo(input);

            if (!isValidImage(input)) {
                return error(HttpStatus.BAD_REQUEST,
                        "Upload a valid PNG or JPEG image with no more than 4 million pixels.");
            }

            Path checkpoint = projectRoot.resolve(
                    "segmentation/checkpoints/full_best.pth"
            );

            if (!Files.isExecutable(pythonExecutable)
                    || !Files.isRegularFile(checkpoint)) {

                return error(HttpStatus.SERVICE_UNAVAILABLE,
                        "The floor plan model is unavailable.");
            }

            // Execute Python directly without constructing a shell command.
            ProcessBuilder builder = new ProcessBuilder(
                    pythonExecutable.toString(),
                    "-m",
                    "segmentation.predict",
                    "--input",
                    input.toString(),
                    "--output",
                    output.toString(),
                    "--checkpoint",
                    checkpoint.toString()
            );

            builder.directory(projectRoot.toFile());
            builder.redirectErrorStream(true);
            builder.redirectOutput(log.toFile());

            process = builder.start();

            boolean completed = process.waitFor(
                    timeoutSeconds, TimeUnit.SECONDS
            );

            if (!completed) {
                process.destroyForcibly();

                return error(HttpStatus.GATEWAY_TIMEOUT,
                        "Floor plan generation timed out.");
            }

            if (process.exitValue() != 0
                    || !Files.isRegularFile(output)) {

                return error(HttpStatus.INTERNAL_SERVER_ERROR,
                        "The floor plan could not be generated.");
            }

            byte[] generatedImage = Files.readAllBytes(output);

            return ResponseEntity.ok()
                    .contentType(MediaType.IMAGE_PNG)
                    .header("Cache-Control", "no-store")
                    .body(generatedImage);

        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();

            return error(HttpStatus.INTERNAL_SERVER_ERROR,
                    "Floor plan generation was interrupted.");

        } catch (IOException | RuntimeException exception) {

            return error(HttpStatus.INTERNAL_SERVER_ERROR,
                    "An error occurred during floor plan generation.");

        } finally {

            if (process != null && process.isAlive()) {
                process.destroyForcibly();

                try {
                    process.waitFor(5, TimeUnit.SECONDS);
                } catch (InterruptedException exception) {
                    Thread.currentThread().interrupt();
                }
            }

            deleteTemporaryFiles(temporaryDirectory);
            generationLock.release();
        }
    }

    private boolean isValidImage(Path input) throws IOException {

        try (ImageInputStream stream =
                     ImageIO.createImageInputStream(input.toFile())) {

            if (stream == null) {
                return false;
            }

            Iterator<ImageReader> readers =
                    ImageIO.getImageReaders(stream);

            if (!readers.hasNext()) {
                return false;
            }

            ImageReader reader = readers.next();

            try {
                reader.setInput(stream, true, true);

                String format = reader.getFormatName();

                if (!format.equalsIgnoreCase("PNG")
                        && !format.equalsIgnoreCase("JPEG")) {
                    return false;
                }

                int width = reader.getWidth(0);
                int height = reader.getHeight(0);

                if (width <= 0 || height <= 0
                        || (long) width * height > MAX_PIXELS) {
                    return false;
                }

                return reader.read(0) != null;

            } finally {
                reader.dispose();
            }
        }
    }

    private ResponseEntity<String> error(
            HttpStatus status, String message) {

        return ResponseEntity.status(status)
                .contentType(MediaType.TEXT_PLAIN)
                .body(message);
    }

    private void deleteTemporaryFiles(Path directory) {

        if (directory == null) {
            return;
        }

        try (Stream<Path> paths = Files.walk(directory)) {

            paths.sorted(Comparator.reverseOrder())
                    .forEach(path -> {
                        try {
                            Files.deleteIfExists(path);
                        } catch (IOException ignored) {
                            // Do not expose internal file paths.
                        }
                    });

        } catch (IOException ignored) {
            // Do not expose internal storage errors.
        }
    }
}
