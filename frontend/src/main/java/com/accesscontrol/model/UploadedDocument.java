package com.accesscontrol.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document(collection = "uploaded_documents")
public class UploadedDocument {

    @Id
    private String id;

    private String originalFilename;
    private String storedFilename;
    private String uploadedBy;
    private Instant uploadedAt;
    private long sizeBytes;

    public UploadedDocument() {
    }

    public UploadedDocument(String originalFilename, String storedFilename,
                            String uploadedBy, long sizeBytes) {
        this.originalFilename = originalFilename;
        this.storedFilename = storedFilename;
        this.uploadedBy = uploadedBy;
        this.uploadedAt = Instant.now();
        this.sizeBytes = sizeBytes;
    }

    public String getId() {
        return id;
    }

    public String getOriginalFilename() {
        return originalFilename;
    }

    public String getStoredFilename() {
        return storedFilename;
    }

    public String getUploadedBy() {
        return uploadedBy;
    }

    public Instant getUploadedAt() {
        return uploadedAt;
    }

    public long getSizeBytes() {
        return sizeBytes;
    }
}
