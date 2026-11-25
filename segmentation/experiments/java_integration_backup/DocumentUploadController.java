package com.accesscontrol;

import com.accesscontrol.model.UploadedDocument;
import com.accesscontrol.repository.UploadedDocumentRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.UUID;

@Controller
public class DocumentUploadController {

    private static final long MAX_TEXT_SIZE = 1L * 1024 * 1024;
    private static final long MAX_IMAGE_SIZE = 5L * 1024 * 1024;

    private final UploadedDocumentRepository documentRepository;
    private final Path uploadDirectory;

    public DocumentUploadController(
            UploadedDocumentRepository documentRepository,
            @Value("${app.upload-dir:./secure-uploads}") String uploadDirectory) {
        this.documentRepository = documentRepository;
        this.uploadDirectory = Path.of(uploadDirectory).toAbsolutePath().normalize();
    }

    @GetMapping("/uploads")
    public String showUploads(Model model) {
        model.addAttribute(
                "documents",
                documentRepository.findAllByOrderByUploadedAtDesc()
        );
        return "uploads";
    }

    @PostMapping("/uploads")
    public String uploadFile(
            @RequestParam("file") MultipartFile file,
            Authentication authentication,
            RedirectAttributes redirectAttributes) {

        if (file.isEmpty()) {
            return fail(redirectAttributes, "Choose a non-empty file.");
        }

        String originalFilename = file.getOriginalFilename();

        if (originalFilename == null || originalFilename.isBlank()) {
            return fail(redirectAttributes, "The filename is invalid.");
        }

        originalFilename = originalFilename.replace('\\', '/');
        originalFilename = originalFilename.substring(
                originalFilename.lastIndexOf('/') + 1
        );
        originalFilename = originalFilename.replaceAll("[\\p{Cntrl}]", "_");

        if (originalFilename.isBlank()) {
            return fail(redirectAttributes, "The filename is invalid.");
        }

        if (originalFilename.length() > 255) {
            originalFilename = originalFilename.substring(0, 255);
        }

        String lowerName = originalFilename.toLowerCase(Locale.ROOT);

        boolean textFile = lowerName.endsWith(".txt");
        boolean imageFile = lowerName.endsWith(".jpg")
                || lowerName.endsWith(".jpeg")
                || lowerName.endsWith(".png")
                || lowerName.endsWith(".webp");

        if (!textFile && !imageFile) {
            return fail(
                    redirectAttributes,
                    "Unsupported file type. Upload .txt, .jpg, .jpeg, .png, or .webp files."
            );
        }

        long sizeLimit = textFile ? MAX_TEXT_SIZE : MAX_IMAGE_SIZE;

        if (file.getSize() > sizeLimit) {
            return fail(
                    redirectAttributes,
                    textFile
                            ? "Text files must be no larger than 1 MB."
                            : "Floorplan images must be no larger than 5 MB."
            );
        }

        byte[] content;

        try {
            content = file.getBytes();

            if (textFile && !isValidText(content)) {
                return fail(
                        redirectAttributes,
                        // Parses through the .txt file to ensure it has acutal plain text.
                        "The .txt file must contain valid UTF-8 plain text."
                );
            }

            if (imageFile && !matchesImageType(content, lowerName)) {
                return fail(
                        redirectAttributes,
                        "The image content does not match its file extension or is invalid."
                );
            }
        } catch (IOException exception) {
            return fail(redirectAttributes, "The file could not be read.");
        }

        String storedExtension = lowerName.substring(lowerName.lastIndexOf('.'));
        String storedFilename = UUID.randomUUID() + storedExtension;
        Path destination = uploadDirectory.resolve(storedFilename).normalize();

        if (!destination.getParent().equals(uploadDirectory)) {
            return fail(redirectAttributes, "The file could not be stored.");
        }

        try {
            Files.createDirectories(uploadDirectory);
            Files.write(destination, content);

            UploadedDocument document = new UploadedDocument(
                    originalFilename,
                    storedFilename,
                    authentication.getName(),
                    content.length
            );

            documentRepository.save(document);

            redirectAttributes.addFlashAttribute(
                    "successMessage", "File uploaded successfully."
            );
        } catch (IOException | RuntimeException exception) {
            try {
                Files.deleteIfExists(destination);
            } catch (IOException ignored) {
                // Keep internal storage errors out of the response.
            }

            return fail(
                    redirectAttributes,
                    "The file could not be saved. Please try again."
            );
        }

        return "redirect:/uploads";
    }

    private boolean isValidText(byte[] content) {
        try {
            String text = StandardCharsets.UTF_8.newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(content))
                    .toString();

            return text.indexOf('\0') < 0;
        } catch (java.nio.charset.CharacterCodingException exception) {
            return false;
        }
    }

    private boolean matchesImageType(byte[] data, String filename) {
        if (filename.endsWith(".png")) {
            byte[] signature = {
                    (byte) 0x89, 'P', 'N', 'G', 0x0D, 0x0A, 0x1A, 0x0A
            };
            return startsWith(data, signature);
        }

        if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) {
            return data.length >= 3
                    && (data[0] & 0xFF) == 0xFF
                    && (data[1] & 0xFF) == 0xD8
                    && (data[2] & 0xFF) == 0xFF;
        }

        if (filename.endsWith(".webp")) {
            return data.length >= 12
                    && asciiAt(data, 0, "RIFF")
                    && asciiAt(data, 8, "WEBP");
        }

        return false;
    }

    private boolean startsWith(byte[] data, byte[] signature) {
        if (data.length < signature.length) {
            return false;
        }

        for (int i = 0; i < signature.length; i++) {
            if (data[i] != signature[i]) {
                return false;
            }
        }

        return true;
    }

    private boolean asciiAt(byte[] data, int offset, String expected) {
        if (data.length < offset + expected.length()) {
            return false;
        }

        for (int i = 0; i < expected.length(); i++) {
            if (data[offset + i] != (byte) expected.charAt(i)) {
                return false;
            }
        }

        return true;
    }

    private String fail(
            RedirectAttributes redirectAttributes,
            String message) {
        redirectAttributes.addFlashAttribute("errorMessage", message);
        return "redirect:/uploads";
    }
}
