## La idea
Aplicación de escritorio para docentes de dibujo técnico y educación tecnológica. El docente describe una figura por texto o adjunta una imagen de referencia (y más adelante por voz) y la app genera la pieza en 3D y sus vistas técnicas: planta, alzado, perfil e isométrica.

- Usuario: una sola docente, que la usa en mi PC de escritorio. No hay acceso remoto ni multiusuario por ahora.
- Visión a futuro: pasar de figuras simples a mecanismos funcionales (engranajes, rieles, poleas, sogas → por ejemplo, un ascensor), para que los docentes diseñen mecanismos que funcionen.

## Decisiones ya tomadas (cuestionalas si ves problemas)
1. Enfoque paramétrico, no generativo: las vistas deben ser exactas, así que no se usan generadores de imágenes.
2. "La IA interpreta, el código calcula": la IA solo traduce el pedido a un JSON estructurado. Las medidas, proyecciones y cálculos los hace siempre código determinista.
3. El JSON se valida con Pydantic antes de construir nada. Si no es válido, se rechaza y se avisa generando un reporte. Este es el arnés de seguridad principal: la IA nunca ejecuta código.
4. Conector de IA intercambiable, para poder cambiar de modelo o proveedor sin tocar el resto.
5. Modo formulario sin IA como respaldo: siempre funciona y sirve para testear el núcleo.
Hardware: Ryzen 7 5700, 32 GB de RAM, RX 6700 XT (12 GB), Windows 11.
7. Interfaz accesible solo desde la propia PC (127.0.0.1).

## Stack previsto
Python 3.11+, Pydantic, CadQuery (y cq_gears en el futuro), Ollama con un modelo local de unos 14B, faster-whisper (voz), pytest + cobertura, ruff, pre-commit + gitleaks, GitHub Actions.

## Roadmap
- Fase 1: figuras simples por texto + imagen de referencia→ 4 vistas + modelo 3D. Modo formulario incluido. (Lo que quiero tener funcionando para la entrega.)
- Fase 2: entrada por voz.
- Fase 3: catálogo de piezas mecánicas (engranajes, ejes, poleas, rieles).
- Fase 4: ensambles con restricciones.
- Fase 5: mecanismos con movimiento y simulación. Aquí la IA propone y el docente valida.

## Documentación esperada
README, CHANGELOG, ADRs (un registro por cada decisión importante), `docs/fuentes.md` (cada librería y modelo con link, versión y licencia), matriz de trazabilidad requisito → tarea → test, y log en JSON de cada pedido (pedido → interpretación → resultado).

## Puntos abiertos donde quiero que me presiones
- Nombre del proyecto.
- Catálogo exacto de figuras de la fase 1 y sus parámetros (prisma, cilindro, agujeros, chaflanes…).
- Unidades y sistema de proyección: en Argentina se usa normalmente el método europeo (ISO E) según normas IRAM. ¿Lo respetamos y cómo lo verificamos?
- ¿Las vistas llevan cotas (medidas) o solo líneas en la fase 1?
- Formatos de salida: SVG, PNG, PDF, STL, STEP.
- Qué pasa cuando la IA interpreta mal el pedido: cómo lo corrige el docente.
- Elección entre Ollama y LM Studio, y qué modelo concreto, considerando el soporte de mi GPU AMD en Windows.
- Criterios de aceptación concretos para la demo de la semana que viene.
- Qué tests son imprescindibles para la entrega y cuáles quedan para después.
- Riesgos del proyecto y cómo mitigarlos.
- Cualquier cosa que no haya considerado.
