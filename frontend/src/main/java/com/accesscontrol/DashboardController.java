package com.accesscontrol;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class DashboardController {

    // Display the floor plan dashboard after login.
    @GetMapping("/")
    public String dashboard() {
        return "dashboard";
    }
}
