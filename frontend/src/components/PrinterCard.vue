<template>
  <!-- Mobile: volle Breite, horizontal. Ab sm: max 280px, vertikal -->
  <div class="ring-foreground/10 bg-card text-card-foreground rounded-lg text-xs/relaxed ring-1 overflow-hidden w-full sm:max-w-xs sm:flex-col flex flex-row">

    <!-- Thumbnail: Höhe = Texthöhe, Breite = Höhe (aspect-square) -->
    <div class="shrink-0 aspect-square self-stretch sm:w-full sm:aspect-square">
      <div class="relative bg-muted/30 flex items-center justify-center w-full h-full">
      <img
        v-if="printerImage"
        :src="printerImage"
        :alt="printer.model"
        class="h-full w-full object-contain p-3"
      />
      <RiPrinterLine v-else class="w-10 h-10 text-muted-foreground/20 sm:w-16 sm:h-16" />

      <!-- Status badge -->
      <div class="absolute top-2 right-2 flex items-center gap-1 bg-background/80 backdrop-blur-sm rounded-full px-1.5 py-0.5">
        <div class="w-1.5 h-1.5 rounded-full shrink-0" :class="statusColor"></div>
        <span class="text-xs font-medium hidden sm:inline">{{ printer.status }}</span>
      </div>
    </div>
    </div>

    <!-- Content -->
    <div class="flex flex-col gap-2 p-3 flex-1 min-w-0">
      <!-- Header -->
      <div class="flex items-start justify-between gap-1">
        <div class="min-w-0">
          <p class="text-sm font-medium truncate">{{ printer.name }}</p>
          <p class="text-xs text-muted-foreground truncate">{{ printer.model }}</p>
          <!-- Status nur auf Mobile sichtbar (weil Badge im Bild versteckt) -->
          <div class="flex items-center gap-1 mt-0.5 sm:hidden">
            <div class="w-1.5 h-1.5 rounded-full shrink-0" :class="statusColor"></div>
            <span class="text-xs text-muted-foreground">{{ printer.status }}</span>
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon" class="h-7 w-7 shrink-0 -mt-0.5 -mr-1">
              <RiMoreLine class="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem @click="$emit('edit', printer)">Bearbeiten</DropdownMenuItem>
            <DropdownMenuItem v-if="printer.purchase_url" @click="openUrl(printer.purchase_url)">
              Nachbestellen
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem class="text-destructive" @click="$emit('delete', printer)">
              Löschen
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-x-3 gap-y-1.5 text-xs">
        <div>
          <p class="text-muted-foreground">IP</p>
          <p class="font-mono font-medium truncate">{{ printer.ip_address }}</p>
        </div>
        <div>
          <p class="text-muted-foreground">Düse</p>
          <p class="font-medium">{{ printer.nozzle_diameter }}mm</p>
        </div>
        <div>
          <p class="text-muted-foreground">AMS</p>
          <p class="font-medium">{{ printer.has_ams ? printer.ams_units.length + ' Einheit(en)' : 'Nein' }}</p>
        </div>
      </div>

      <!-- AMS slots (nur vertikal / sm+) -->
      <div v-if="printer.has_ams && printer.ams_units.length > 0" class="border-t border-border pt-2 space-y-2 hidden sm:block">
        <p class="text-xs text-muted-foreground">AMS Slots</p>
        <div v-for="ams in printer.ams_units" :key="ams.id" class="space-y-1">
          <p class="text-xs font-medium">{{ ams.type.toUpperCase() }} #{{ ams.ams_index + 1 }}</p>
          <div class="flex gap-1">
            <div
              v-for="slot in ams.slots"
              :key="slot.id"
              class="flex-1 h-5 rounded-sm border border-border text-xs flex items-center justify-center"
              :class="slot.spool_id ? 'bg-primary/20' : 'bg-muted'"
            >
              {{ slot.slot_index + 1 }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { RiPrinterLine, RiMoreLine } from '@remixicon/vue'
import type { Printer } from '@/types/printer'

const props = defineProps<{ printer: Printer }>()
defineEmits<{ edit: [printer: Printer]; delete: [printer: Printer] }>()

const printerImages: Record<string, string> = {
  'Bambu Lab A1':      '/printers/a1.png',
  'Bambu Lab A1 mini': '/printers/a1-mini.png',
  'Bambu Lab P1P':     '/printers/p1p.png',
  'Bambu Lab P1S':     '/printers/p1s.png',
  'Bambu Lab X1C':     '/printers/x1c.png',
  'Bambu Lab X1E':     '/printers/x1e.png',
}

const printerImage = computed(() => printerImages[props.printer.model] ?? null)

const statusColor = computed(() => ({
  'bg-green-500':        props.printer.status === 'online',
  'bg-blue-500':         props.printer.status === 'printing',
  'bg-yellow-500':       props.printer.status === 'idle',
  'bg-red-500':          props.printer.status === 'error',
  'bg-muted-foreground': props.printer.status === 'offline',
}))

const openUrl = (url: string | null) => { if (url) window.open(url, '_blank') }
</script>