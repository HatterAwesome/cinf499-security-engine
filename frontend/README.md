# Access Control Operations
This README is assumed and meant for the System Integrator during system installation and monitoring

A Java Spring Boot web application for managing a simulated physical access control system. Built for CSEC 302 Secure Coding.

## Features

- Login and role-based access for administrators and operators
- Dashboard showing door status and recent access events
- Create and edit doors
- Search and filter access events
- Create, edit, and delete user accounts
- Upload floorplan images and text files
- Input validation and secure error handling

## Technologies

- Java 21
- Spring Boot
- Spring Security
- MongoDB
- Thymeleaf
- Bootstrap
- Maven

## Setup

You will need Java 21, Maven, and MongoDB.

1. Start MongoDB.
2. Set the administrator credentials in your terminal:

   ```bash
   export APP_ADMIN_USERNAME=admin
   export APP_ADMIN_PASSWORD='your-strong-password'
   ```

3. If needed, set your MongoDB connection string:

   ```bash
   export MONGODB_URI='mongodb://localhost:27017/accesscontrol_db'
   ```

4. Start the application:

   ```bash
   mvn spring-boot:run
   ```

5. Open http://localhost:8080 and log in with the administrator credentials you configured.

## Security

- Spring Security handles login, logout, and role-based access.
- Passwords are hashed with BCrypt.
- Door and user forms use server-side input validation.
- Spring Data MongoDB repositories handle database operations.
- File uploads are restricted to `.txt`, `.jpg`, `.jpeg`, `.png`, and `.webp`.
- Text files are limited to 1 MB and images to 5 MB.
- Uploaded files use generated storage names and are stored outside the public static directory.
- Thymeleaf `th:text` escapes displayed values to help prevent XSS.
- Error settings prevent default responses from including exception details and stack traces.

## Testing

Run the build with:

```bash
mvn clean test
```

Manual testing has covered login, role restrictions, door and user management, event filtering, file type validation, and file size limits.

There are currently no automated test cases.

## Notes

This application uses simulated access-control data. It does not control real doors or security hardware.

## CINF 499 Senior Research Integration

The dashboard supports AI-assisted floor plan labeling.

### Current Functionality

- Authenticated floor plan analysis
- PNG and JPEG image uploads
- Original and generated image comparison
- U-Net semantic segmentation
- OpenCV architectural boundary refinement
- English room label rendering
- Generated PNG download

### Integrated Application Setup

From the repository root:

    python3.11 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r segmentation/requirements.txt

Configure the model connection:

    export FLOORPLAN_PROJECT_ROOT="$(pwd)"
    export FLOORPLAN_PYTHON="$FLOORPLAN_PROJECT_ROOT/.venv/bin/python"
    export MONGODB_URI='mongodb://localhost:27017/accesscontrol_db'

Configure APP_ADMIN_USERNAME and APP_ADMIN_PASSWORD
using your own administrator credentials.

Start MongoDB and run:

    cd frontend
    mvn spring-boot:run

Open http://localhost:8080 and sign in.

The trained checkpoint is included in the repository.
Retraining is not required.

### Backend Integration

    POST /api/floorplans/generate

Java ProcessBuilder executes the Python prediction
pipeline and returns a generated PNG to the browser.

### Generation Safeguards

- Authentication and CSRF protection
- PNG and JPEG content validation
- Maximum upload size of 5 MB
- Maximum image area of 4 million pixels
- Processing timeout of 120 seconds
- Single concurrent model execution
- Temporary file cleanup
- Generic error responses

### Research Limitations

Predicted room labels require human verification.
Incorrect classifications and missing labels may occur.

The system does not automatically place access control
devices or control physical security hardware.
