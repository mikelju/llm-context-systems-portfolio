<!-- Spec §3.2. Mermaid renders on GitHub. Keep it readable. -->
# Architecture Diagram

```mermaid
flowchart TD
    A[Inputs] --> B[Stage 1]
    B --> C[Stage 2]
    C --> D[(State / catalog / index)]
    D --> E{Decision}
    E -->|branch 1| F[...]
    E -->|branch 2| G[...]
```
