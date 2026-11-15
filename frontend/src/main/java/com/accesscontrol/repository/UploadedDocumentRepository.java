package com.accesscontrol.repository;

import com.accesscontrol.model.UploadedDocument;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface UploadedDocumentRepository
        extends MongoRepository<UploadedDocument, String> {

    List<UploadedDocument> findAllByOrderByUploadedAtDesc();
}
