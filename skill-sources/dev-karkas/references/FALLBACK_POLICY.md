# Fallback policy

Fallback должен быть спроектирован, а не добавлен как случайный `try/catch`.

## Для каждой optional/unstable dependency определи

1. Primary path.
2. Failure signals.
3. Fallback path.
4. Когда fallback запрещён из-за риска неправильного результата.
5. User-visible behavior.
6. Telemetry/diagnostics.
7. Recovery / retry policy.
8. Performance/cost degradation.

## Типичные примеры

```text
GPU/CUDA/OpenCL/WebGPU unavailable
→ CPU fallback
→ тот же контракт результата
→ возможно медленнее
→ telemetry records backend=cpu_fallback
```

```text
LLM/provider unavailable
→ alternate model/provider или deterministic mode
→ только если semantic contract приемлем
→ иначе explicit unavailable error
```

```text
cache unavailable
→ source-of-truth path
→ не терять correctness ради cache
```

## Не делай fallback, если он скрывает corruption

Не продолжай молча при:

- schema mismatch;
- failed authorization;
- corrupted persistent data;
- invalid cryptographic verification;
- incompatible file version, когда нет доказанного converter;
- partial destructive migration.

В таких случаях fail closed / explicit error обычно безопаснее.

## Anti-cascade

Fallback не должен создавать каскадную нагрузку. Например, массовый cache miss не должен бесконтрольно обрушивать primary database. Используй concurrency limits, queue/backpressure и circuit-breaker-подобную логику, когда оправдано.
