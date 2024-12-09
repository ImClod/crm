<template>
    <div>
      <LayoutHeader>
        <template #left-header>
          <div class="flex items-center gap-2">
            <h1 class="text-xl font-bold">{{ __('Scheduled Calls') }}</h1>
          </div>
        </template>
        <template #right-header>
          <div class="flex items-center gap-2">
            <ViewControls 
              :doctype="doctype"
              :filters="filters"
            />
          </div>
        </template>
      </LayoutHeader>
  
      <ListView
        :columns="columns"
        :rows="rows"
        :options="{
          getRowRoute: (row) => ({
            name: 'Contact',
            params: { name: row.name }
          }),
          selectable: false
        }"
      >
        <ListHeader class="sm:mx-5 mx-3">
          <ListHeaderItem
            v-for="column in columns"
            :key="column.key"
            :item="column"
          />
        </ListHeader>
        
        <ListRows :rows="rows" v-slot="{ column, item, row }">
          <ListRowItem :item="item">
            <template #default="{ label }">
              <div 
                v-if="column.key === 'actions'" 
                class="flex items-center space-x-2"
              >
                <Tooltip :text="__('Mark Call Completed')">
                  <Button 
                    variant="solid" 
                    class="bg-green-500 hover:bg-green-600"
                    @click="markCallStatus(row, 'Completed')"
                  >
                    <CheckIcon class="w-4 h-4" />
                  </Button>
                </Tooltip>
                <Tooltip :text="__('Mark Call Rejected')">
                  <Button 
                    variant="solid" 
                    class="bg-red-500 hover:bg-red-600"
                    @click="markCallStatus(row, 'Rejected')"
                  >
                    <DeclinedCallIcon class="w-4 h-4" />
                  </Button>
                </Tooltip>
              </div>
              <div v-else>{{ label }}</div>
            </template>
          </ListRowItem>
        </ListRows>
      </ListView>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { 
    createResource, 
    Tooltip, 
    Button 
  } from 'frappe-ui'
  import { useRouter } from 'vue-router'
  import CheckIcon from '@/components/Icons/CheckIcon.vue'
  import DeclinedCallIcon from '@/components/Icons/DeclinedCallIcon.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import ListView from '@/components/ListView.vue'
  import ListHeader from '@/components/ListHeader.vue'
  import ListHeaderItem from '@/components/ListHeaderItem.vue'
  import ListRows from '@/components/ListRows.vue'
  import ListRowItem from '@/components/ListRowItem.vue'
  
  const doctype = 'Contact'
  const router = useRouter()
  
  // Definisci le colonne
  const columns = [
    { 
      label: 'Name', 
      key: 'full_name', 
      type: 'Data', 
      width: '20rem' 
    },
    { 
      label: 'Email', 
      key: 'email', 
      type: 'Data', 
      width: '15rem' 
    },
    { 
      label: 'Mobile', 
      key: 'mobile_no', 
      type: 'Data', 
      width: '12rem' 
    },
    { 
      label: 'Actions', 
      key: 'actions', 
      type: 'Data', 
      width: '10rem' 
    }
  ]
  
  // Risorse API
  const list = ref(createResource({
    url: 'crm.api.doc.get_data',
    params: {
      doctype: doctype,
      filters: {},
      order_by: 'modified desc'
    },
    cache: ['Scheduled Calls'],
    auto: true
  }))
  
  const rows = computed(() => {
    return list.value.data?.data || []
  })
  
  const filters = ref({})
  
  const markCallStatusResource = createResource({
    url: 'crm.api.contact.mark_call_status',
    method: 'POST',
    onSuccess: (response) => {
      // Ricarica la lista dopo aver segnato la chiamata
      list.value.reload()
    },
    onError: (error) => {
      console.error('Error marking call status:', error)
    }
  })
  
  // Marca stato chiamata
  const markCallStatus = (row, status) => {
    markCallStatusResource.submit({
      contact: row.name,
      status: status
    })
  }
  
  // Gestore evento real-time
  const handleRealtimeUpdate = (data) => {
    list.value.reload()
  }
  
  onMounted(() => {
    // Registra listener per aggiornamenti real-time
    frappe.realtime.on('scheduled_call_updated', handleRealtimeUpdate)
  })
  
  onUnmounted(() => {
    // Rimuovi listener
    frappe.realtime.off('scheduled_call_updated', handleRealtimeUpdate)
  })
  </script>