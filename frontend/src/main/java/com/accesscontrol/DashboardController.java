package com.accesscontrol;

import com.accesscontrol.model.AccessEvent;
import com.accesscontrol.model.Door;
import com.accesscontrol.repository.AccessEventRepository;
import com.accesscontrol.repository.DoorRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
public class DashboardController {

    private final DoorRepository doorRepository;
    private final AccessEventRepository accessEventRepository;

    public DashboardController(
            DoorRepository doorRepository,
            AccessEventRepository accessEventRepository) {
        this.doorRepository = doorRepository;
        this.accessEventRepository = accessEventRepository;
    }

    @GetMapping("/")
    public String dashboard(Model model) {
        List<Door> doors = doorRepository.findAll();

        long doorsOnline = doors.stream()
                .filter(door -> door.getStatus() != null)
                .filter(door -> !door.getStatus().equals("OFFLINE"))
                .count();

        List<AccessEvent> recentEvents = accessEventRepository.findAll();

        model.addAttribute("systemName", "Access Control Operations");
        model.addAttribute("totalDoors", doors.size());
        model.addAttribute("doorsOnline", doorsOnline);
        model.addAttribute("doorsOffline", doors.size() - doorsOnline);
        model.addAttribute("recentEvents", recentEvents.stream()
                .limit(5)
                .toList());

        // Incident management is not implemented yet.
        model.addAttribute("openIncidents", 3);
        model.addAttribute("incidentsSimulated", true);

        return "dashboard";
    }
}
