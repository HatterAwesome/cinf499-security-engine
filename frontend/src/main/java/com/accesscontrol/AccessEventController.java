package com.accesscontrol;

import com.accesscontrol.model.AccessEvent;
import com.accesscontrol.repository.AccessEventRepository;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.Locale;

@Controller
public class AccessEventController {

    private final AccessEventRepository eventRepository;

    public AccessEventController(AccessEventRepository eventRepository) {
        this.eventRepository = eventRepository;
    }

    @GetMapping("/events")
    public String events(
            @RequestParam(required = false, defaultValue = "") String search,
            @RequestParam(required = false, defaultValue = "ALL") String result,
            Model model) {

        List<AccessEvent> allEvents = eventRepository.findAll(
                Sort.by(Sort.Direction.DESC, "timestamp"));

        String searchTerm = search.trim().toLowerCase(Locale.ROOT);

        if (!result.equals("ALL")
                && !result.equals("GRANTED")
                && !result.equals("DENIED")) {
            result = "ALL";
        }

        final String selectedResult = result;

        List<AccessEvent> filteredEvents = allEvents.stream()
                .filter(event -> selectedResult.equals("ALL")
                        || selectedResult.equals(event.getResult()))
                .filter(event -> searchTerm.isBlank()
                        || contains(event.getDoorName(), searchTerm)
                        || contains(event.getPersonName(), searchTerm)
                        || contains(event.getDetails(), searchTerm))
                .toList();

        long grantedCount = allEvents.stream()
                .filter(event -> "GRANTED".equals(event.getResult()))
                .count();

        long deniedCount = allEvents.stream()
                .filter(event -> "DENIED".equals(event.getResult()))
                .count();

        model.addAttribute("events", filteredEvents);
        model.addAttribute("search", search);
        model.addAttribute("selectedResult", result);
        model.addAttribute("totalEvents", allEvents.size());
        model.addAttribute("grantedCount", grantedCount);
        model.addAttribute("deniedCount", deniedCount);

        return "events";
    }

    private boolean contains(String value, String searchTerm) {
        return value != null
                && value.toLowerCase(Locale.ROOT).contains(searchTerm);
    }
}
