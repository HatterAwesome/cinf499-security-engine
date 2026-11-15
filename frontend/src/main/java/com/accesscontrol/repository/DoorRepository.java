package com.accesscontrol.repository;

import com.accesscontrol.model.Door;
import org.springframework.data.mongodb.repository.MongoRepository;

// Provides database operations for doors.
public interface DoorRepository extends MongoRepository<Door, String> {
}
