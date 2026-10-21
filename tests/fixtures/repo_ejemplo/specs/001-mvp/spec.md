# Feature Specification: Artemis — MVP Modelo 3D desde Formulario

**Feature Branch**: `001-mvp-modelo-formulario`

**Created**: 2026-10-18

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE ofrecer un formulario con los campos necesarios para definir
  un prisma rectangular (largo, ancho, alto) o un cilindro (diámetro, alto).
- **FR-004**: El sistema DEBE generar el modelo 3D con las medidas exactas indicadas, con
  tolerancia geométrica de 0,001 mm.
- **FR-005**: El sistema DEBE rechazar cualquier combinación de parámetros inválidos
  (medida ≤ 0, diámetro de agujero ≥ lado menor de la cara, agujero fuera del área de la
  cara) con un mensaje que identifique el problema específico, antes de iniciar la
  construcción.
- **FR-006**: El sistema DEBE exportar el modelo en STL y STEP al workspace configurado.
