<template>
    <Dialog v-model="show" :options="{ title: __('Scheduled Call Details'), size: 'xl' }">
      <template #body-content>
        <div v-if="call" class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-3">
            <div class="flex items-center gap-3">
              <ContactIcon class="h-5 w-5 text-gray-600" />
              <div>
                <div class="text-base font-semibold">{{ __('Contact') }}</div>
                <div>{{ call.full_name || 'N/A' }}</div>
              </div>
            </div>
  
            <div class="flex items-center gap-3">
              <PhoneIcon class="h-5 w-5 text-gray-600" />
              <div>
                <div class="text-base font-semibold">{{ __('Phone') }}</div>
                <div>{{ call.mobile_no || 'N/A' }}</div>
              </div>
            </div>
  
            <div class="flex items-center gap-3">
              <InboxIcon class="h-5 w-5 text-gray-600" />
              <div>
                <div class="text-base font-semibold">{{ __('Email') }}</div>
                <div>{{ call.email || 'N/A' }}</div>
              </div>
            </div>
          </div>
  
          <div class="flex flex-col gap-3">
            <div class="flex items-center gap-3">
              <CalendarIcon class="h-5 w-5 text-gray-600" />
              <div>
                <div class="text-base font-semibold">{{ __('Scheduled Date') }}</div>
                <div>{{ call.custom_first_date || 'N/A' }}</div>
              </div>
            </div>
  
            <div class="flex items-center gap-3">
              <ClockIcon class="h-5 w-5 text-gray-600" />
              <div>
                <div class="text-base font-semibold">{{ __('Status') }}</div>
                <div>{{ call.status || 'N/A' }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center text-gray-500">
          {{ __('No call details available') }}
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import { 
    Dialog, 
  } from 'frappe-ui'
  
  import ContactIcon from '@/components/Icons/ContactIcon.vue'
  import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
  import InboxIcon from '@/components/Icons/InboxIcon.vue'
  import CalendarIcon from '@/components/Icons/CalendarIcon.vue'
  import ClockIcon from '@/components/Icons/ClockIcon.vue'
  
  const props = defineProps({
    call: {
      type: Object,
      default: () => ({})
    }
  })
  
  const show = defineModel()
  </script>