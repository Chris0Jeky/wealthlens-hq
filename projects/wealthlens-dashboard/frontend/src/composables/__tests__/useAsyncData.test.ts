import { describe, it, expect, vi } from "vitest"
import { useAsyncData } from "@/composables/useAsyncData"

describe("useAsyncData", () => {
  it("starts with null data and no loading", () => {
    const { data, loading, error } = useAsyncData(() => Promise.resolve("test"))
    expect(data.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it("sets loading to true during execution", async () => {
    let resolve!: (v: string) => void
    const fetcher = () =>
      new Promise<string>((r) => {
        resolve = r
      })

    const { loading, execute } = useAsyncData(fetcher)
    const promise = execute()
    expect(loading.value).toBe(true)

    resolve("done")
    await promise
    expect(loading.value).toBe(false)
  })

  it("sets data on success", async () => {
    const { data, execute } = useAsyncData(() => Promise.resolve({ items: [1, 2] }))
    await execute()
    expect(data.value).toEqual({ items: [1, 2] })
  })

  it("sets error on failure", async () => {
    const { error, data, execute } = useAsyncData(() => Promise.reject(new Error("Server error")))
    await execute()
    expect(error.value).toBe("Server error")
    expect(data.value).toBeNull()
  })

  it("clears error on retry", async () => {
    const fetcher = vi.fn().mockRejectedValueOnce(new Error("fail")).mockResolvedValueOnce("ok")

    const { data, error, execute } = useAsyncData(fetcher)

    await execute()
    expect(error.value).toBe("fail")

    await execute()
    expect(error.value).toBeNull()
    expect(data.value).toBe("ok")
  })

  it("handles non-Error throws", async () => {
    const { error, execute } = useAsyncData(() => Promise.reject("string error"))
    await execute()
    expect(error.value).toBe("An unexpected error occurred")
  })
})
