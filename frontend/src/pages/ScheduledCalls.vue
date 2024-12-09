<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold">{{ __('Scheduled Calls') }}</h1>
      </div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-2">
        <input
          type="text"
          v-model="searchQuery"
          :placeholder="__('Search contacts...')"
          class="rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>
    </template>
  </LayoutHeader>

  <div class="flex-1 overflow-auto p-4">
    <div v-if="loading" class="flex h-full items-center justify-center">
      <div class="text-gray-600">{{ __('Loading...') }}</div>
    </div>
    <div v-else-if="!filteredContacts.length" class="flex h-full items-center justify-center">
      <div class="text-center text-gray-600">
        <ContactsIcon class="mx-auto h-12 w-12 text-gray-400" />
        <p class="mt-2">{{ __('No scheduled calls for today') }}</p>
      </div>
    </div>
    <div v-else class="space-y-4">
      <div v-for="contact in filteredContacts" :key="contact.name" 
        class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <div class="flex items-center justify-between">
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
            </div>
          </div>
          <div class="flex gap-2">
            <Button
              variant="solid"
              class="bg-green-600 hover:bg-green-700"
              :label="__('Completed')"
              @click="markCallCompleted(contact)"
            />
            <Button
              variant="solid"
              class="bg-red-600 hover:bg-red-700"
              :label="__('Rejected')"
              @click="markCallRejected(contact)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import ContactsIcon from '../components/Icons/ContactsIcon.vue'

const router = useRouter()
const loading = ref(true)
const contacts = ref([])
const searchQuery = ref('')

const scheduledCalls = createResource({
  url: 'crm.api.contact.get_scheduled_calls',
  onSuccess: (data) => {
    contacts.value = data
    loading.value = false
  },
  onError: (error) => {
    console.error('Error fetching scheduled calls:', error)
    loading.value = false
  },
})

const filteredContacts = computed(() => {
  if (!searchQuery.value) return contacts.value
  const query = searchQuery.value.toLowerCase()
  return contacts.value.filter(contact => 
    contact.full_name.toLowerCase().includes(query) ||
    (contact.email && contact.email.toLowerCase().includes(query)) ||
    (contact.mobile_no && contact.mobile_no.includes(query))
  )
})

const markCallCompleted = async (contact) => {
  try {
    await createResource({
      url: 'crm.api.contact.mark_call_completed',
      method: 'POST',
      data: {
        contact: contact.name,
        status: 'Completed'
      },
    }).submit()
    
    // Remove contact from the list
    contacts.value = contacts.value.filter(c => c.name !== contact.name)
  } catch (error) {
    console.error('Error marking call as completed:', error)
  }
}

const markCallRejected = async (contact) => {
  try {
    await createResource({
      url: 'crm.api.contact.mark_call_rejected',
      method: 'POST',
      data: {
        contact: contact.name,
        status: 'Rejected'
      },
    }).submit()
    
    // Remove contact from the list
    contacts.value = contacts.value.filter(c => c.name !== contact.name)
  } catch (error) {
    console.error('Error marking call as rejected:', error)
  }
}

onMounted(() => {
  scheduledCalls.fetch()
})
</script>
