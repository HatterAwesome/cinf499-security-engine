package com.accesscontrol;

import com.accesscontrol.model.Door;
import com.accesscontrol.repository.DoorRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;

// Adds example doors the first time the application starts.
@Component
public class DoorDataInitializer implements CommandLineRunner {

    private final DoorRepository doorRepository;

    public DoorDataInitializer(DoorRepository doorRepository) {
        this.doorRepository = doorRepository;
    }

    @Override
    public void run(String... args) {
        // Do not add duplicates if doors already exist.
        if (doorRepository.count() > 0) {
            System.out.println("Door records already exist. Skipping sample data.");
            return;
        }

        List<Door> sampleDoors = List.of(
            new Door("Main Entrance", "Building A - Lobby", "SECURE"),
            new Door("Server Room", "Building A - IT Room", "SECURE"),
            new Door("Employee Entrance", "Building A - Rear Entry", "UNLOCKED"),
            new Door("Loading Dock", "Building A - Receiving", "OFFLINE"),
            new Door("Office Floor 2", "Building A - Second Floor", "SECURE")
        );

        doorRepository.saveAll(sampleDoors);
        System.out.println("Five sample door records created.");
    }
}
