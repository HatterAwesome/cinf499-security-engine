package com.accesscontrol.repository;

import com.accesscontrol.model.AccessEvent;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface AccessEventRepository
        extends MongoRepository<AccessEvent, String> {
}
