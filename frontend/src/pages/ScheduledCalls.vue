<template>
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-2">
          <h1 class="text-xl font-bold">{{ __('Today\'s Scheduled Calls') }}</h1>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <!-- Barra di ricerca -->
          <Input
            type="text"
            v-model="searchQuery"
            :placeholder="__('Search contacts...')"
            class="w-64"
          />
        </div>
      </template>
    </LayoutHeader>
  
    <div class="p-4">
      <!-- Stato di caricamento -->
      <div v-if="loading" class="flex justify-center items-center h-full">
        <Spinner />
      </div>
  
      <!-- Lista vuota -->
      <div 
        v-else-if="filteredContacts.length === 0" 
        class="flex flex-col items-center justify-center h-full text-gray-500"
      >
        <ContactsIcon class="h-16 w-16 mb-4" />
        <p>{{ __('No scheduled calls for today') }}</p>
      </div>
  
      <!-- Lista contatti -->
      <div v-else class="space-y-4">
        <div 
          v-for="contact in filteredContacts" 
          :key="contact.name"
          class="bg-white border rounded-lg p-4 flex justify-between items-center shadow-sm"
        >
          <div class="flex-1">
            <router-link 
              :to="{ name: 'Contact', params: { name: contact.name } }"
              class="text-lg font-semibold text-blue-600 hover:text-blue-800"
            >
              {{ contact.full_name }}
            </router-link>
            <div class="text-sm text-gray-600 mt-1">
              <div>{{ contact.email }}</div>
              <div>{{ contact.mobile_no }}</div>
            </div>
          </div>
  
          <div class="flex space-x-2">
            <Tooltip :text="__('Mark Call Completed')">
              <Button 
                variant="solid" 
                class="bg-green-500 hover:bg-green-600"
                @click="markCallStatus(contact, 'Completed')"
              >
                <CheckIcon class="w-5 h-5" />
              </Button>
            </Tooltip>
  
            <Tooltip :text="__('Mark Call Rejected')">
              <Button 
                variant="solid" 
                class="bg-red-500 hover:bg-red-600"
                @click="markCallStatus(contact, 'Rejected')"
              >
                <DeclinedCallIcon class="w-5 h-5" />
              </Button>
            </Tooltip>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { createResource, Tooltip, Button } from 'frappe-ui'
  import { useRouter } from 'vue-router'
  import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
  import CheckIcon from '@/components/Icons/CheckIcon.vue'
  import DeclinedCallIcon from '@/components/Icons/DeclinedCallIcon.vue'
  
  const router = useRouter()
  const loading = ref(true)
  const contacts = ref([])
  const searchQuery = ref('')
  
  // Risorse API
  const scheduledCalls = createResource({
    url: 'crm.api.contact.get_scheduled_calls',
    onSuccess: (data) => {
      contacts.value = data
      loading.value = false
    },
    onError: (error) => {
      console.error('Error fetching scheduled calls:', error)
      loading.value = false
    }
  })
  
  const markCallStatusResource = createResource({
    url: 'crm.api.contact.mark_call_status',
    method: 'POST',
    onSuccess: (response) => {
      // La rimozione del contatto avverrà tramite evento realtime
    },
    onError: (error) => {
      console.error('Error marking call status:', error)
    }
  })
  
  // Filtro contatti
  const filteredContacts = computed(() => {
    return contacts.value.filter(contact => 
      !searchQuery.value || 
      contact.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      contact.email.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      contact.mobile_no.includes(searchQuery.value)
    )
  })
  
  // Marca stato chiamata
  const markCallStatus = (contact, status) => {
    markCallStatusResource.submit({
      contact: contact.name,
      status: status
    })
  }
  
  // Gestore evento real-time
  const handleRealtimeUpdate = (data) => {
    contacts.value = contacts.value.filter(c => c.name !== data.contact)
  }
  
  onMounted(() => {
    scheduledCalls.fetch()
    
    // Registra listener per aggiornamenti real-time
    frappe.realtime.on('scheduled_call_updated', handleRealtimeUpdate)
  })
  
  onUnmounted(() => {
    // Rimuovi listener
    frappe.realtime.off('scheduled_call_updated', handleRealtimeUpdate)
  })
  </script>