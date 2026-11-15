package com.accesscontrol;

import com.accesscontrol.model.AppUser;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

// Provides database operations for application users.
public interface AppUserRepository extends MongoRepository<AppUser, String> {

    Optional<AppUser> findByUsername(String username);
}
