<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <p class="text-sm text-muted-foreground">{{ printers.length }} Drucker konfiguriert</p>
      <Button size="sm" @click="openCreate">
        <RiAddLine class="w-4 h-4 mr-2" />
        Drucker hinzufügen
      </Button>
    </div>

    <div v-if="loading" class="text-sm text-muted-foreground">Laden...</div>

    <div v-else-if="printers.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
      <RiPrinterLine class="w-12 h-12 text-muted-foreground/30 mb-4" />
      <p class="text-sm font-medium">Noch keine Drucker</p>
      <p class="text-xs text-muted-foreground mt-1">Füge deinen ersten Drucker hinzu</p>
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <Card v-for="printer in printers" :key="printer.id" class="relative">
        <CardHeader class="pb-2">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full mt-1 shrink-0" :class="statusColor(printer.status)"></div>
              <div>
                <CardTitle class="text-base">{{ printer.name }}</CardTitle>
                <p class="text-xs text-muted-foreground">{{ printer.model }}</p>
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" class="h-8 w-8">
                  <RiMoreLine class="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem @click="openEdit(printer)">Bearbeiten</DropdownMenuItem>
                <DropdownMenuItem v-if="printer.purchase_url" @click="openUrl(printer.purchase_url)">
                  Nachbestellen
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem class="text-destructive" @click="confirmDelete(printer)">
                  Löschen
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        <CardContent class="space-y-3">
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
              <p class="text-muted-foreground">Status</p>
              <Badge :variant="statusVariant(printer.status)" class="text-xs">{{ printer.status }}</Badge>
            </div>
            <div>
              <p class="text-muted-foreground">AMS</p>
              <p class="font-medium">{{ printer.has_ams ? printer.ams_units.length + ' Einheit(en)' : 'Nein' }}</p>
            </div>
          </div>

          <!-- AMS slots -->
          <div v-if="printer.has_ams && printer.ams_units.length > 0" class="border-t border-border pt-3">
            <p class="text-xs text-muted-foreground mb-2">AMS Slots</p>
            <div v-for="ams in printer.ams_units" :key="ams.id" class="mb-2">
              <p class="text-xs font-medium mb-1">{{ ams.type.toUpperCase() }} #{{ ams.ams_index + 1 }}</p>
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
        </CardContent>
      </Card>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="dialogOpen">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{{ editingPrinter ? 'Drucker bearbeiten' : 'Drucker hinzufügen' }}</DialogTitle>
        </DialogHeader>
        <form @submit.prevent="savePrinter" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <Label>Name</Label>
              <Input v-model="form.name" placeholder="Drucker 1" required />
            </div>
            <div class="space-y-1">
              <Label>Modell</Label>
              <Select v-model="form.model">
                <SelectTrigger><SelectValue placeholder="Modell wählen" /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="m in printerModels" :key="m" :value="m">{{ m }}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <Label>IP-Adresse</Label>
              <Input v-model="form.ip_address" placeholder="192.168.1.100" required />
            </div>
            <div class="space-y-1">
              <Label>Access Code</Label>
              <Input v-model="form.access_code" placeholder="12345678" required />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <Label>Seriennummer</Label>
              <Input v-model="form.serial_number" placeholder="Optional" />
            </div>
            <div class="space-y-1">
              <Label>Düsendurchmesser (mm)</Label>
              <Input v-model.number="form.nozzle_diameter" type="number" step="0.1" placeholder="0.4" />
            </div>
          </div>
          <div class="space-y-1">
            <Label>Nachbestell-Link</Label>
            <Input v-model="form.purchase_url" placeholder="https://..." />
          </div>
          <div class="flex items-center gap-2">
            <Switch
                :model-value="form.has_ams"
                @update:model-value="(val: boolean) => form.has_ams = val"
            />
            <Label>Hat AMS / Multi-Material System</Label>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" @click="dialogOpen = false">Abbrechen</Button>
            <Button type="submit" :disabled="saving">{{ saving ? 'Speichern...' : 'Speichern' }}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { RiAddLine, RiPrinterLine, RiMoreLine } from '@remixicon/vue'
import { printersApi } from '@/api/printers'
import type { Printer as PrinterType } from '@/types/printer'

const printers = ref<PrinterType[]>([])
const loading = ref(true)
const dialogOpen = ref(false)
const saving = ref(false)
const editingPrinter = ref<PrinterType | null>(null)

const printerModels = ['Bambu Lab A1', 'Bambu Lab A1 mini', 'Bambu Lab P1P', 'Bambu Lab P1S', 'Bambu Lab X1C', 'Bambu Lab X1E']

const form = reactive({
  name: '',
  model: '',
  serial_number: '',
  ip_address: '',
  access_code: '',
  nozzle_diameter: 0.4,
  has_ams: false,
  purchase_url: '',
})

const resetForm = () => {
  form.name = ''
  form.model = ''
  form.serial_number = ''
  form.ip_address = ''
  form.access_code = ''
  form.nozzle_diameter = 0.4
  form.has_ams = false
  form.purchase_url = ''
}

const openCreate = () => {
  editingPrinter.value = null
  resetForm()
  dialogOpen.value = true
}

const openEdit = (printer: PrinterType) => {
  editingPrinter.value = printer
  form.name = printer.name
  form.model = printer.model
  form.serial_number = printer.serial_number ?? ''
  form.ip_address = printer.ip_address
  form.access_code = printer.access_code
  form.nozzle_diameter = printer.nozzle_diameter
  form.has_ams = printer.has_ams
  form.purchase_url = printer.purchase_url ?? ''
  dialogOpen.value = true
}

const savePrinter = async () => {
  saving.value = true

  try {
    const data = {
      name: form.name,
      model: form.model,
      serial_number: form.serial_number || undefined,
      ip_address: form.ip_address,
      access_code: form.access_code,
      nozzle_diameter: form.nozzle_diameter,
      has_ams: form.has_ams,
      purchase_url: form.purchase_url || undefined,
    }
    if (editingPrinter.value) {
      await printersApi.update(editingPrinter.value.id, data)
    } else {
      await printersApi.create(data)
    }
    await loadPrinters()
    dialogOpen.value = false
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (printer: PrinterType) => {
  if (confirm(`Drucker "${printer.name}" wirklich löschen?`)) {
    await printersApi.delete(printer.id)
    await loadPrinters()
  }
}

const openUrl = (url: string | null) => { if (url) window.open(url, '_blank') }

const statusColor = (status: string) => ({
  'bg-green-500': status === 'online',
  'bg-blue-500': status === 'printing',
  'bg-yellow-500': status === 'idle',
  'bg-red-500': status === 'error',
  'bg-muted-foreground': status === 'offline',
})

const statusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  if (status === 'error') return 'destructive'
  if (status === 'offline') return 'secondary'
  return 'outline'
}

const loadPrinters = async () => {
  const { data } = await printersApi.getAll()
  printers.value = data
}

onMounted(async () => {
  try { await loadPrinters() } finally { loading.value = false }
})
</script>
