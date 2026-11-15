package com.accesscontrol;

import com.accesscontrol.model.Door;
import com.accesscontrol.repository.DoorRepository;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;
import java.util.Set;

@Controller
@RequestMapping("/doors")
public class DoorController {

    private static final Set<String> ALLOWED_STATUSES =
            Set.of("SECURE", "UNLOCKED", "OFFLINE");

    private final DoorRepository doorRepository;

    public DoorController(DoorRepository doorRepository) {
        this.doorRepository = doorRepository;
    }

    @GetMapping
    public String showDoors(Model model) {
        List<Door> doors = doorRepository.findAll();
        model.addAttribute("doors", doors);
        return "doors";
    }

    @GetMapping("/new")
    public String newDoor(Model model) {
        model.addAttribute("door", new Door());
        model.addAttribute("pageTitle", "Add Door");
        return "door-form";
    }

    @PostMapping
    public String createDoor(
            @Valid Door door,
            BindingResult result,
            RedirectAttributes redirectAttributes) {

        validateStatus(door, result);

        if (result.hasErrors()) {
            return "door-form";
        }

        // Ignore any client-supplied ID when creating a new record.
        door.setId(null);
        doorRepository.save(door);

        redirectAttributes.addFlashAttribute(
                "successMessage", "Door added successfully.");
        return "redirect:/doors";
    }

    @GetMapping("/{id}/edit")
    public String editDoor(@PathVariable String id, Model model) {
        return doorRepository.findById(id)
                .map(door -> {
                    model.addAttribute("door", door);
                    model.addAttribute("pageTitle", "Edit Door");
                    return "door-form";
                })
                .orElse("redirect:/doors");
    }

    @PostMapping("/{id}/edit")
    public String updateDoor(
            @PathVariable String id,
            @Valid Door submittedDoor,
            BindingResult result,
            RedirectAttributes redirectAttributes) {

        validateStatus(submittedDoor, result);

        if (result.hasErrors()) {
            submittedDoor.setId(id);
            return "door-form";
        }

        return doorRepository.findById(id)
                .map(existingDoor -> {
                    existingDoor.setName(submittedDoor.getName().trim());
                    existingDoor.setLocation(submittedDoor.getLocation().trim());
                    existingDoor.setStatus(submittedDoor.getStatus());

                    doorRepository.save(existingDoor);
                    redirectAttributes.addFlashAttribute(
                            "successMessage", "Door updated successfully.");
                    return "redirect:/doors";
                })
                .orElse("redirect:/doors");
    }

    private void validateStatus(Door door, BindingResult result) {
        if (door.getStatus() == null
                || !ALLOWED_STATUSES.contains(door.getStatus())) {
            result.rejectValue(
                    "status", "door.status.invalid",
                    "Choose a valid door status.");
        }
    }
}
