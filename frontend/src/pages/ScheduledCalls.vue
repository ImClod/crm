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
          <input
            type="text"
            v-model="searchQuery"
            :placeholder="__('Search contacts...')"
            class="rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          
          <!-- Filtri aggiuntivi -->
          <select 
            v-model="callStatusFilter" 
            class="rounded-lg border border-gray-300 px-3 py-2"
          >
            <option value="">{{ __('All Calls') }}</option>
            <option value="pending">{{ __('Pending') }}</option>
            <option value="scheduled">{{ __('Scheduled') }}</option>
          </select>
        </div>
      </template>
    </LayoutHeader>
  
    <div class="flex-1 overflow-auto p-4">
      <!-- Stato di caricamento -->
      <div v-if="loading" class="flex h-full items-center justify-center">
        <div class="text-gray-600">{{ __('Loading calls...') }}</div>
      </div>
  
      <!-- Stato vuoto -->
      <div v-else-if="!filteredContacts.length" class="flex h-full items-center justify-center">
        <div class="text-center text-gray-600">
          <ContactsIcon class="mx-auto h-12 w-12 text-gray-400" />
          <p class="mt-2">{{ __('No scheduled calls for today') }}</p>
        </div>
      </div>
  
      <!-- Lista dei contatti -->
      <div v-else class="space-y-4">
        <div 
          v-for="contact in filteredContacts" 
          :key="contact.name" 
          class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
        >
          <div class="flex items-center justify-between">
            <!-- Informazioni contatto -->
            <div class="flex-1">
              <router-link 
                :to="{ name: 'Contact', params: { name: contact.name }}"
                class="text-lg font-medium text-blue-600 hover:text-blue-800"
              >
                {{ contact.full_name }}
              </router-link>
              <div class="mt-1 text-sm text-gray-600">
                <div>{{ contact.email }}</div>
                <div>{{ contact.mobile_no }}</div>
                <div class="mt-1 font-semibold text-gray-700">
                  {{ __('Scheduled Time') }}: {{ formatScheduledTime(contact.scheduled_time) }}
                </div>
              </div>
            </div>
  
            <!-- Azioni per la chiamata -->
            <div class="flex gap-2">
              <Tooltip :text="__('Mark Call Completed')">
                <Button
                  variant="solid"
                  class="bg-green-600 hover:bg-green-700"
                  @click="showConfirmModal(contact, 'completed')"
                >
                  <CheckIcon class="h-5 w-5" />
                </Button>
              </Tooltip>
              
              <Tooltip :text="__('Mark Call Rejected')">
                <Button
                  variant="solid"
                  class="bg-red-600 hover:bg-red-700"
                  @click="showConfirmModal(contact, 'rejected')"
                >
                  <DeclinedCallIcon class="h-5 w-5" />
                </Button>
              </Tooltip>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Modal di conferma -->
      <Dialog 
        v-if="confirmModalVisible" 
        @close="confirmModalVisible = false"
      >
        <template #title>
          {{ __('Confirm Call Status') }}
        </template>
        <template #content>
          {{ __('Are you sure you want to mark this call as') }} 
          {{ currentAction === 'completed' ? __('completed') : __('rejected') }}?
        </template>
        <template #actions>
          <Button 
            variant="ghost" 
            @click="confirmModalVisible = false"
          >
            {{ __('Cancel') }}
          </Button>
          <Button 
            variant="solid" 
            :class="currentAction === 'completed' ? 'bg-green-600' : 'bg-red-600'"
            @click="confirmCallStatus"
          >
            {{ __('Confirm') }}
          </Button>
        </template>
      </Dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { createResource } from 'frappe-ui'
  import { useRouter } from 'vue-router'
  import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
  import CheckIcon from '@/components/Icons/CheckIcon.vue'
  import DeclinedCallIcon from '@/components/Icons/DeclinedCallIcon.vue'
  
  const router = useRouter()
  const loading = ref(true)
  const contacts = ref([])
  const searchQuery = ref('')
  const callStatusFilter = ref('')
  const confirmModalVisible = ref(false)
  const currentContact = ref(null)
  const currentAction = ref('')
  
  // Risorse per le chiamate API
  const scheduledCalls = createResource({
    url: 'crm.api.contact.get_scheduled_calls',
    onSuccess: (data) => {
      contacts.value = data
      loading.value = false
    },
    onError: (error) => {
      console.error('Error fetching scheduled calls:', error)
      loading.value = false
      // Aggiungi gestione errore con toast/notifica
    },
  })
  
  // Filtro contatti con ricerca e filtri
  const filteredContacts = computed(() => {
    return contacts.value.filter(contact => {
      const matchesSearch = !searchQuery.value || 
        contact.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        (contact.email && contact.email.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
        (contact.mobile_no && contact.mobile_no.includes(searchQuery.value))
      
      const matchesStatusFilter = !callStatusFilter.value || 
        contact.call_status === callStatusFilter.value
      
      return matchesSearch && matchesStatusFilter
    })
  })
  
  // Mostra modal di conferma
  const showConfirmModal = (contact, action) => {
    currentContact.value = contact
    currentAction.value = action
    confirmModalVisible.value = true
  }
  
  // Conferma stato chiamata
  const confirmCallStatus = async () => {
    try {
      const resource = createResource({
        url: currentAction.value === 'completed' 
          ? 'crm.api.contact.mark_call_completed' 
          : 'crm.api.contact.mark_call_rejected',
        method: 'POST',
        data: {
          contact: currentContact.value.name,
          status: currentAction.value === 'completed' ? 'Completed' : 'Rejected'
        },
      })
      
      await resource.submit()
      
      // Rimuovi contatto dalla lista
      contacts.value = contacts.value.filter(c => c.name !== currentContact.value.name)
      
      // Chiudi modal
      confirmModalVisible.value = false
    } catch (error) {
      console.error(`Error marking call as ${currentAction.value}:`, error)
      // Aggiungi gestione errore con toast/notifica
    }
  }
  
  // Formatta il tempo programmato per la chiamata
  const formatScheduledTime = (scheduledTime) => {
    const date = new Date(scheduledTime)
    return date.toLocaleString() // Formattazione della data e ora
  }
  
  onMounted(() => {
    scheduledCalls.fetch()
  })
  </script>