NetGraphIQ: Network Topology Discovery & Behavioral Anomaly Detection

    Transforming network visibility through graph intelligence and real-time behavioral anomaly detection.

Problem Statement :

   Intelligent Network Topology Discovery & Anomaly Detection :
      Modern IoT and enterprise networks are highly dynamic, making it difficult for administrators to:
        1.Understand real-time network topology
        2.Identify relationships between devices
        3.Detect abnormal behavior such as traffic spikes, rogue devices, or failures

      Existing solutions often rely on manual configuration or lack intelligent insights, resulting in delayed detection and increased operational risk.

Proposed Solution :

    NetGraphIQ is an intelligent system that:
        1.Simulates a network environment with interconnected devices
        2.Automatically discovers network topology using inferred signals (ARP/neighbor-based logic)
        3.Models the network as a graph structure
        4.Continuously generates and monitors telemetry data
        5.Detects anomalies using rule-based and machine learning techniques
        6.Provides real-time visualization and insights through an interactive dashboard

Key Features :

    1.Automated topology discovery (ARP-inspired inference)
    2.Graph-based network modeling using NetworkX
    3.Real-time telemetry simulation and monitoring
    4.Behavioral anomaly detection (traffic spikes, device failures, rogue activity)
    5.Interactive dashboard with visual network representation
    6.Event timeline and anomaly explanation system (planned enhancement)

System Architecture & Data Flow :

    Simulation Layer → Discovery Engine → Graph Builder → Telemetry Generator → Anomaly Detection → Dashboard

Tech Stack :

    Python
    NetworkX (Graph Modeling)
    Streamlit (Interactive Dashboard)
    Scikit-learn (Anomaly Detection)
    Pandas (Data Processing)

Project Structure :
    src/
    ├── core/            # Simulation, discovery, graph, telemetry logic
    ├── detection/       # Anomaly detection engine
    └── ui/              # Dashboard and visualization

    data/                 # Telemetry and logs
    docs/                 # Architecture diagrams
    main.py               # Entry point

Setup Instructions :

    1.Clone the repository:
      git clone https://github.com/Gladson-git/H2H-Error202-NetGraphIQ
      cd NetGraphIQ

    2.Install dependencies:
      pip install -r requirements.txt

    3.Run the application:
      python main.py

Current Status :
    Day 1 — Project initialization, architecture definition, and repository setup completed.


Team Members :
    Gladson K
    Rahul Balan

Deployment :
    The application will be deployed and made accessible via a live link by the end of the build phase.

Demo / Screenshots :
    Visual demonstrations and a walkthrough video will be included once the system is fully functional.

    