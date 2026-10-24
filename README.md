# Hospital Management & Patient Billing System

An Object-Oriented Hospital and Patient Billing Management System developed in Java. The project models real-world hospital workflows, integrating department organization, doctor compensation, and dynamic medical billing structures.

## 🏗️ Core OOP Architectural Principles
- **Abstraction & Interfaces (`billable`, `patientBase`):** Decoupled billing logic and enforced structured contracts across diverse patient categories.
- **Inheritance & Specialization (`emergencyPatient`, `longTermPatient`):** Extended baseline patient records to accommodate specific billing criteria.
- **Polymorphism:** Streamlined billing aggregation across heterogeneous collections without runtime type inspections or downcasting (`instanceof`).
- **Encapsulation:** Protected entity invariants via private fields and validated mutators/accessors.
- **Sorting & Object Comparison (`Comparable<T>`):** Leveraged Java collections sorting to rank doctors by salary and patients by total healthcare billings.

## 📂 Project Structure
- `billable.java`: Interface defining billing rates and calculation contracts.
- `patientBase.java`: Abstract base class modeling core patient attributes.
- `emergencyPatient.java`: Specialized class for emergency admissions.
- `longTermPatient.java`: Specialized class for extended inpatient care.
- `hospitalService.java`: Medical service representation (X-Ray, MRI, Labs).
- `doctor.java`: Staff record with degree-based overtime and salary logic.
- `department.java`: Department container tracking assigned doctors and patients.
- `driver.java`: Entry point demonstrating runtime polymorphism and sorting.

## 🚀 Build & Run
```bash
javac Project/*.java
java Project.driver