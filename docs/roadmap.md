# Features & Roadmap

The project is being developed in **modular phases** to ensure usability, scalability, and cross-platform compatibility. Any step or features listed below is subject to change in the future, nothing is set in stone as of yet.

## 1. Basics: Core Network Tools (Windows 10 & 11)

- Develop Python scripts for:
    - Network port scanning
    - Static IP address assignment
    - MAC address lookup
    - Connectivity tests (ping, traceroute, etc.)
    - Other essential AV-over-IP tasks
- Ensure scripts are modular and field-tested for practical use

## 2. User Interface (Windows 10 & 11)

- Develop a UI using Python (Tkinter or PyQT)
- Implement a tab-based design with expandable toolbars for future features
- Integrate previously developed scripts into the UI

## 3. Documentation Management

- Store job-based documentation, including:
    - Field notes
    - Service reports
    - Before-and-after installation photos
    - Troubleshooting records
- Introduce a PostgreSQL database to manage stored documentation
- Allow global note editing for specific manufacturer devices

## 4. Cross-Platform Compatibility
- Expand application support to Mac and Linux
- Refactor all scripts to ensure cross-platform functionality.

## 5. Cloud-Based Application
- Transition the app from a local install to a web-based platform
- Implement a login system for organizations and individuals
- Host all scripts, databases, and web resources using AWS or any cloud hosting site
- Select and integrate a scalable web framework (Python Django but open to other options)

## 6. Knowledge Base & Training Resources
- Develop a built-in knowledge base with:
    - AV and IT terminology definitions
    - Industry news and best practices
    - Links to manufacturer training portals and certification programs

## 7. Finishing Touches & Refinements
- Implement final improvements based on field feedback and testing
