<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold">{{ __('Scheduled Calls') }}</h1>
      </div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-2">
        <DateRangePicker 
          v-model="dateRange"
          @change="updateDateFilter"
        />
      </div>
    </template>
  </LayoutHeader>

  <ScheduledCallsListView
    :rows="formattedRows"
    :columns="columns"
    :options="{
      rowCount: list.data?.row_count || 0,
      totalCount: list.data?.total_count || 0,
      selectable: true,
      showTooltip: true,
      resizeColumn: true,
    }"
    @showScheduledCall="navigateToContact"
    @loadMore="loadMore"
  >
    <template #actions="{ row }">
      <div class="flex gap-2">
        <Button
          variant="solid"
          theme="green"
          size="sm"
          :label="__('Confirm')"
          @click="markCallStatus(row, 'Confirmed')"
        >
          <template #prefix>
            <CheckIcon class="w-4 h-4" />
          </template>
        </Button>
        <Button
          variant="solid"
          theme="red"
          size="sm"
          :label="__('Reject')"
          @click="markCallStatus(row, 'Canceled')"
        >
          <template #prefix>
            <XIcon class="w-4 h-4" />
          </template>
        </Button>
      </div>
    </template>
  </ScheduledCallsListView>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource, call, Button } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import ScheduledCallsListView from '@/components/ListViews/ScheduledCallsListView.vue'
import DateRangePicker from '@/components/DateRangePicker.vue'
import CheckIcon from '@/components/Icons/CheckIcon.vue'
import XIcon from '@/components/Icons/XIcon.vue'

const router = useRouter()
const toast = useToast()

// Stato per i filtri
const dateRange = ref(null)

// Risorsa per la lista delle chiamate programmate
const list = createResource({
  url: 'crm.api.contact.get_scheduled_calls',
  params: {},
  auto: true
})

// Definisci le colonne
const columns = ref([
  { 
    key: 'full_name', 
    label: 'Contact Name', 
    type: 'Link',
    width: '16rem'
  },
  { 
    key: 'mobile_no', 
    label: 'Mobile No', 
    type: 'Data',
    width: '12rem'
  },
  { 
    key: 'custom_first_date', 
    label: 'Call Status', 
    type: 'Data',
    width: '12rem'
  },
  { 
    key: 'actions', 
    label: 'Actions', 
    type: 'Custom',
    width: '15rem'
  }
])

// Formatta le righe per aggiungere informazioni personalizzate
const formattedRows = computed(() => {
  return (list.data || []).map(call => ({
    ...call,
    full_name: call.full_name || 'Unknown',
    mobile_no: call.mobile_no || 'N/A',
    custom_first_date: call.custom_first_date || 'Not Scheduled'
  }))
})

// Navigazione al contatto quando si clicca su una riga
function navigateToContact(row) {
  if (row.contact_link) {
    router.push(row.contact_link)
  }
}

// Marcare lo stato della chiamata
async function markCallStatus(row, status) {
  try {
    const result = await call('crm.api.contact.mark_call_status', {
      contact: row.full_name,
      status: status
    })

    if (result.status === 'success') {
      toast.success(result.message)
      // Ricarica la lista delle chiamate
      list.reload()
    } else {
      toast.error(result.message)
    }
  } catch (error) {
    console.error('Error marking call status:', error)
    toast.error('An error occurred while updating call status')
  }
}

// Caricamento di più elementi
function loadMore() {
  list.reload()
}

// Funzione per aggiornare i filtri data
function updateDateFilter() {
  // Logica per aggiornare i filtri in base alla selezione della data
}
</script>