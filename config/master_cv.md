# Resume

## Education

B.Eng in Mechatronics Engineering Co-op  
McMaster University, Hamilton, Ontario  
Sep 2021 - Aug 2026

- Coursework: Embedded, Robotics, DSP, RTOS, DSA | Formula Electric (Software & Controls)

## Work Experience

AI & Full Stack Developer Intern  
Nestlé Canada, Toronto, ON  
May 2024 - Dec 2025  
Python, LangGraph, LangChain, MCP, Azure, SQL, React, TypeScript, Tailwind, GitHub Actions

- Engineered a multi-agent LLM orchestration system (Python, LangGraph) to automate large-scale competitor data extraction from disparate web and email sources, generating executive summaries and driving $750K in annual operational savings.
- Architected and deployed a 4-tier microservices backend on Azure, decoupling web scraping, REST API routing, and NLP categorization; implemented data deduplication algorithms to ensure high data fidelity and pipeline freshness.
- Architected and shipped a production React and TypeScript web application serving 500+ enterprise users, engineering complex product-line data mapping and dynamic subscription-management workflows.
- Optimized LLM inference latency and eliminated context window saturation by integrating the Model Context Protocol (MCP) with structured SQL databases and categorical search indexing.
- Prototyped and containerized (Docker) a Server-Side Rendered (SSR) data visualization microservice in <8 hours, enabling LLM agents to dynamically generate interactive business charts from natural language queries.
- Reduced deployment failure rate by 40% by authoring modular GitHub Actions CI/CD pipelines, automating testing and enabling zero-downtime releases to Azure Web Apps.
- Designed an enterprise HR onboarding chatbot utilizing a category-based RAG architecture; leveraged LangGraph semantic routing and a React/Tailwind frontend to deliver highly accurate, citation-backed query resolution.

Full Stack Developer  
Chase Auto Parts, Mississauga, ON  
Sep 2023 - Apr 2024  
Azure, n8n, LangGraph, SQL, React, TypeScript, Electron, Node.js, Express.js

- Reduced part-identification errors by 57% by developing a real-time, 2-tier AI assistant (LangGraph, RAG); processed live audio transcripts to dynamically extract entity parameters and inject stateful guided prompts into the employee UI.
- Developed a cross-platform desktop application (Electron, React, TypeScript) featuring a custom dynamic screen overlay engine, automating step-by-step UI navigation for complex legacy POS workflows.
- Slashed cloud compute costs by 40% ($12K/year) by re-architecting legacy POS integration infrastructure; developed a custom Node.js CLI tool to optimize data synchronization and binary distribution.
- Engineered a location-aware conversational agent via n8n, orchestrating RAG-based document retrieval over complex return policies with RESTful Google Maps API integrations to deliver context-aware customer support.
- Hardened legacy POS database access by constructing a secure Node.js/Express.js REST API, enforcing strict schema validation and Role-Based Access Control (RBAC) for all internal clients.

Mobile Developer  
Fanique Group, Toronto, ON  
May 2023 - Aug 2023  
React, Flutter, Dart, Figma, Mobile Development

- Accelerated cross-platform release velocity by **40%** by engineering **Flutter** mobile applications with a shared Dart codebase, delivering production builds to both **iOS and Android** from a single CI/CD pipeline.
- Increased user engagement by **25%** (measured via session duration and interaction depth analytics) by developing responsive, component-based web interfaces in **React** with dynamic state management and optimized re-render strategies.
- Reduced frontend development time for new features by **30%** by standardizing a **reusable component library** of 20+ UI primitives, enforcing design-token consistency across web and mobile surfaces.
- Translated high-fidelity **Figma** prototypes into pixel-perfect implementations, collaborating with designers to maintain a living design system with documented spacing, typography, and colour tokens.
- Improved mobile app performance scores (Lighthouse / Flutter DevTools) by **15%** by profiling widget rebuilds, lazy-loading heavy assets, and implementing platform-adaptive UI patterns for iOS and Android.

## Projects

Conformal-Cashflow – Uncertainty-Aware Liquidity Forecasting  
PyTorch, LangGraph, Docker, SQL, Conformal Prediction, Temporal Fusion Transformers

- Achieved **90% conformal coverage (PICP)** in liquidity forecasting by architecting a **two-stage Hurdle Model** (Classification Gate + Quantile Head) to provide statistically rigorous confidence intervals for enterprise treasury management.
- Scaled training to **1.1 million transaction records** (COFINFAD dataset) by implementing **per-account local normalization** and **Dilated 1D Convolutions**, capturing long-range monthly trends while handling extreme account heterogeneity.
- Mitigated "flat-line" signal washout in sparse financial logs by engineering a **Sequence Sharpness Loss** (Volume, Variance, Temporal Correlation) and integrating **Direct Lag Injection** to force historical rhythm awareness.
- Optimized temporal feature capture using **Cyclical Time Encodings** and **Spectral (FFT) Analysis** to model seasonality, achieving high sharpness (low MPIW) while maintaining a mathematical guarantee on prediction reliability.
- Ensured production-grade reliability by building a **Dockerized GPU-accelerated pipeline** and achieving **100% pass rate across a 37-test suite** covering unit and integration testing.

RouteWise – AI-Powered Fuel Efficiency Predictor  
Python, LightGBM, Random Forest, Optuna, SHAP, SQLite

- Achieved **0.84 $R^2$** in fuel economy prediction (improving from 0.42 baseline) by architecting a **two-stage cascaded AI pipeline** to decouple latent traffic congestion from vehicle physics.
- Engineered a **Physics-Informed Ensemble (LightGBM + Random Forest)** using **Vehicle Specific Power (VSP)** to model aerodynamic drag and inertial losses across 260+ vehicles in the **eVED dataset**.
- Optimized spatial feature engineering by building a **1km segment engine** with **SQLite-cached elevation data**, increasing enrichment efficiency and capturing local grade impacts on energy consumption.
- Quantified model interpretability and drove performance gains by implementing **SHAP explanations** and **Optuna-based Bayesian hyperparameter tuning**.

StrideSense - Automated Cow Disease Detection (Capstone)  
CATTLEytics Inc.  
Python, C++, OpenCV, PyTorch, MQTT, Edge AI

- Achieved over 85% lameness detection accuracy by training custom **CNNs** (PyTorch) on McMaster University's GPU cluster (8x NVIDIA V100) and engineering a **C++/Python** pipeline with offline-first architecture.
- Implemented ear tag detection (**YOLOv5**) and pose estimation to identify each cow and calculate lameness metrics (spinal tilt, head bobbing), integrated with a local web dashboard and **MQTT** sync to cloud.
- Designed a **rugged hardware enclosure** supporting 1,000 lbs to ensure continuous operation in barn environments.

HIL Telemetry & Control System  
McMaster University (McMaster Formula Electric)  
Go, React, WebSockets, CAN Bus, REST API

- **Architected a low-latency Hardware-in-the-Loop (HIL) and Software-in-the-Loop (SIL) simulation framework** in **Go** to validate real-time control algorithms and state machine logic for custom EV powertrain ECUs.
- **Engineered a high-throughput, persistent TCP/IP server architecture** utilizing concurrent goroutines to handle synchronous firmware logic requests, achieving sub-50ms round-trip latency for real-time telemetry processing.
- **Designed a deterministic test execution engine** that dynamically parses **YAML** configurations to instantiate virtual vehicle states, memory structs, and I/O mappings without requiring binary recompilation.
- **Automated hardware fault injection and edge-case validation** by implementing state-matching algorithms that simulate discrete/analog sensor data, generating programmatic **HTML** trace logs to verify strict functional safety requirements.
- **Developed a robust CLI test orchestrator** to streamline the validation pipeline, enabling rapid iterative testing of the Vehicle Control Unit (VCU) and integration into automated CI/CD workflows.

## Skills

Programming  
Python, TypeScript, JavaScript, C++, C#, Visual Basic, SQL, Go, Dart, C, Java, PHP, Kotlin, Swift, MATLAB

Frameworks  
React, React Native, Vue, Angular, Flutter, Spring Boot, Symfony, .NET, TensorFlow, PyTorch, Pandas, OpenCV, LightGBM, Optuna, SHAP, LangChain, LangGraph, n8n, Node.js

Technologies  
Azure, AWS, Google Cloud, Linux, Unix, Docker, Kubernetes, Jenkins, GitHub Actions, CI/CD, YAML, RAG, Agentic AI, MCP, CLI, Git, Figma, Jira, Terraform
