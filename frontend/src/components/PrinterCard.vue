<template>
  <div class="ring-foreground/10 bg-card text-card-foreground rounded-lg text-xs/relaxed ring-1 overflow-hidden flex flex-col">
    <!-- Thumbnail -->
    <div class="relative w-full aspect-square bg-muted/30 flex items-center justify-center">
      <img
        v-if="printerImage"
        :src="printerImage"
        :alt="printer.model"
        class="h-full w-full object-contain p-4"
      />
      <RiPrinterLine v-else class="w-16 h-16 text-muted-foreground/20" />
      <!-- Status badge overlay -->
      <div class="absolute top-2 right-2 flex items-center gap-1.5 bg-background/80 backdrop-blur-sm rounded-full px-2 py-1">
        <div class="w-1.5 h-1.5 rounded-full" :class="statusColor"></div>
        <span class="text-xs font-medium">{{ printer.status }}</span>
      </div>
    </div>

    <!-- Content -->
    <div class="flex flex-col gap-3 p-3">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <p class="text-sm font-medium">{{ printer.name }}</p>
          <p class="text-xs text-muted-foreground">{{ printer.model }}</p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon" class="h-7 w-7 -mt-0.5 -mr-1">
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
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div>
          <p class="text-muted-foreground">IP</p>
          <p class="font-mono font-medium">{{ printer.ip_address }}</p>
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

      <!-- AMS slots -->
      <div v-if="printer.has_ams && printer.ams_units.length > 0" class="border-t border-border pt-3 space-y-2">
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
  'Bambu Lab A1':     '/printers/a1.png',
  'Bambu Lab A1 mini':'/printers/a1-mini.png',
  'Bambu Lab P1P':    '/printers/p1p.png',
  'Bambu Lab P1S':    '/printers/p1s.png',
  'Bambu Lab X1C':    '/printers/x1c.png',
  'Bambu Lab X1E':    '/printers/x1e.png',
}

const printerImage = computed(() => printerImages[props.printer.model] ?? null)

const statusColor = computed(() => ({
  'bg-green-500': props.printer.status === 'online',
  'bg-blue-500':  props.printer.status === 'printing',
  'bg-yellow-500':props.printer.status === 'idle',
  'bg-red-500':   props.printer.status === 'error',
  'bg-muted-foreground': props.printer.status === 'offline',
}))

const openUrl = (url: string | null) => { if (url) window.open(url, '_blank') }
</script>
