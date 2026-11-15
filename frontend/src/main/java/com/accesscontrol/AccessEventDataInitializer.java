package com.accesscontrol;

import com.accesscontrol.model.AccessEvent;
import com.accesscontrol.repository.AccessEventRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class AccessEventDataInitializer implements CommandLineRunner {

    private final AccessEventRepository eventRepository;

    public AccessEventDataInitializer(AccessEventRepository eventRepository) {
        this.eventRepository = eventRepository;
    }

    @Override
    public void run(String... args) {
        // Only add sample events when the collection is empty.
        if (eventRepository.count() > 0) {
            return;
        }

        LocalDateTime now = LocalDateTime.now();

        eventRepository.save(new AccessEvent(
                "Main Entrance", "Alex Morgan", "GRANTED",
                "Valid employee credentials", now.minusMinutes(5)));

        eventRepository.save(new AccessEvent(
                "Server Room", "Jordan Lee", "DENIED",
                "Insufficient access permissions", now.minusMinutes(12)));

        eventRepository.save(new AccessEvent(
                "Employee Entrance", "Taylor Smith", "GRANTED",
                "Valid employee credentials", now.minusMinutes(20)));

        eventRepository.save(new AccessEvent(
                "Loading Dock", "Unknown User", "DENIED",
                "Unrecognized credential", now.minusMinutes(35)));

        eventRepository.save(new AccessEvent(
                "Server Room", "Casey Brown", "DENIED",
                "Access attempt outside authorized permissions", now.minusMinutes(50)));

        System.out.println("Five sample access events created.");
    }
}
