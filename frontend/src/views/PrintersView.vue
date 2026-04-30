<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <p class="text-sm text-muted-foreground">{{ printers.length }} Drucker konfiguriert</p>
      <div class="flex items-center gap-2">
        <ViewToggle v-model="viewMode" />
        <Tooltip>
          <TooltipTrigger as-child>
            <Button size="icon" @click="openCreate">
              <RiAddLine class="w-4 h-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Drucker hinzufügen</TooltipContent>
        </Tooltip>
      </div>
    </div>

    <div v-if="loading" class="text-sm text-muted-foreground">Laden...</div>

    <div v-else-if="printers.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
      <RiPrinterLine class="w-12 h-12 text-muted-foreground/30 mb-4" />
      <p class="text-sm font-medium">Noch keine Drucker</p>
      <p class="text-xs text-muted-foreground mt-1">Füge deinen ersten Drucker hinzu</p>
    </div>

    <!-- Grid view -->
    <div v-else-if="viewMode === 'grid'" class="grid gap-4 grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
      <PrinterCard
        v-for="printer in printers"
        :key="printer.id"
        :printer="printer"
        @edit="openEdit"
        @delete="confirmDelete"
      />
    </div>

    <!-- List view -->
    <div v-else>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead class="w-4"></TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Modell</TableHead>
            <TableHead>IP</TableHead>
            <TableHead>Düse</TableHead>
            <TableHead>AMS</TableHead>
            <TableHead>Status</TableHead>
            <TableHead></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="printer in printers" :key="printer.id">
            <TableCell>
              <div class="w-2 h-2 rounded-full" :class="statusColor(printer.status)"></div>
            </TableCell>
            <TableCell class="font-medium">{{ printer.name }}</TableCell>
            <TableCell class="text-muted-foreground">{{ printer.model }}</TableCell>
            <TableCell class="font-mono text-xs">{{ printer.ip_address }}</TableCell>
            <TableCell>{{ printer.nozzle_diameter }}mm</TableCell>
            <TableCell>{{ printer.has_ams ? printer.ams_units.length + ' Einheit(en)' : '—' }}</TableCell>
            <TableCell>
              <Badge :variant="statusVariant(printer.status)" class="text-xs">{{ printer.status }}</Badge>
            </TableCell>
            <TableCell>
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
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
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
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { RiAddLine, RiPrinterLine, RiMoreLine } from '@remixicon/vue'
import { printersApi } from '@/api/printers'
import type { Printer as PrinterType } from '@/types/printer'
import ViewToggle from '@/components/ViewToggle.vue'
import PrinterCard from '@/components/PrinterCard.vue'

const printers = ref<PrinterType[]>([])
const loading = ref(true)
const dialogOpen = ref(false)
const saving = ref(false)
const editingPrinter = ref<PrinterType | null>(null)
const viewMode = ref<'grid' | 'list'>('grid')

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

const openCreate = () => { editingPrinter.value = null; resetForm(); dialogOpen.value = true }

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
