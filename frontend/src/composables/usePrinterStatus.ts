import { ref, onMounted, onUnmounted } from 'vue'

export interface PrinterStatus {
  // Interner Online-Status vom Backend
  _online?: boolean

  // Druckstatus
  gcode_state?: string        // 'IDLE' | 'RUNNING' | 'PAUSE' | 'FINISH' | 'FAILED'
  mc_percent?: number         // Fortschritt 0–100
  mc_remaining_time?: number  // Verbleibende Zeit in Minuten
  subtask_name?: string       // Dateiname des aktuellen Drucks

  // Temperaturen
  nozzle_temper?: number
  nozzle_target_temper?: number
  bed_temper?: number
  bed_target_temper?: number
  chamber_temper?: number

  // Lüfter (0–15 Bambu-Skala → /15 * 100 = %)
  cooling_fan_speed?: number  // Bauteilkühlung
  big_fan1_speed?: number     // Aux-Lüfter
  big_fan2_speed?: number     // Kammerlüfter

  // Sonstiges
  wifi_signal?: string
  spd_lvl?: number            // 1=Ruhig 2=Normal 3=Sport 4=Turbo
  layer_num?: number
  total_layer_num?: number
}

export function usePrinterStatus(printerId: number) {
  const status = ref<PrinterStatus | null>(null)
  const isConnected = ref(false)
  const wsConnected = ref(false)

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  function connect() {
    const host = window.location.hostname
    const url = `ws://${host}:8000/ws/printers/${printerId}`
    ws = new WebSocket(url)

    ws.onopen = () => {
      wsConnected.value = true
      console.log(`WS Drucker ${printerId} verbunden`)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.ping) return  // Keepalive ignorieren

      status.value = data
      // _online kommt vom Backend; fallback: wenn wir Daten bekommen → online
      isConnected.value = data._online !== false
    }

    ws.onclose = () => {
      wsConnected.value = false
      isConnected.value = false
      reconnectTimer = setTimeout(connect, 5000)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  onMounted(connect)
  onUnmounted(() => {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws?.close()
  })

  return { status, isConnected, wsConnected }
}