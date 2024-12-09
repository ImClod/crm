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
            <DateRangePicker 
              v-model="filters.date_range.value"
              @change="updateDateFilter"
            />
          </div>
        </template>
      </LayoutHeader>
  
      <div v-if="scheduledCallsResource.loading" class="flex justify-center items-center h-64">
        <LoadingIndicator />
      </div>
  
      <div v-else-if="rows.length === 0" class="flex justify-center items-center h-64 text-gray-500">
        {{ __('No scheduled calls for today') }}
      </div>
  
      <div v-else class="overflow-x-auto">
        <div class="w-full">
          <div class="bg-white shadow-md rounded-lg overflow-hidden">
            <div class="min-w-full">
              <div class="grid grid-cols-5 bg-gray-100 border-b">
                <div class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ __('Name') }}
                </div>
                <div class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ __('Email') }}
                </div>
                <div class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ __('Mobile') }}
                </div>
                <div class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ __('First Call Date') }}
                </div>
                <div class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {{ __('Actions') }}
                </div>
              </div>
              <div>
                <div 
                  v-for="row in rows" 
                  :key="row.name" 
                  class="grid grid-cols-5 border-b hover:bg-gray-50 transition"
                >
                  <div class="px-4 py-3 whitespace-nowrap">{{ row.full_name }}</div>
                  <div class="px-4 py-3 whitespace-nowrap">{{ row.email }}</div>
                  <div class="px-4 py-3 whitespace-nowrap">{{ row.mobile_no }}</div>
                  <div class="px-4 py-3 whitespace-nowrap">{{ row.custom_first_date }}</div>
                  <div class="px-4 py-3 whitespace-nowrap flex items-center space-x-2">
                    <Tooltip :text="__('Mark Call Completed')">
                      <Button 
                        variant="solid" 
                        class="bg-green-500 hover:bg-green-600 !p-1 !h-8 !w-8 flex items-center justify-center"
                        @click="markCallStatus(row, 'Completed')"
                      >
                        <CheckIcon class="w-4 h-4" />
                      </Button>
                    </Tooltip>
                    <Tooltip :text="__('Mark Call Rejected')">
                      <Button 
                        variant="solid" 
                        class="bg-red-500 hover:bg-red-600 !p-1 !h-8 !w-8 flex items-center justify-center"
                        @click="markCallStatus(row, 'Rejected')"
                      >
                        <DeclinedCallIcon class="w-4 h-4" />
                      </Button>
                    </Tooltip>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { 
    createResource, 
    Tooltip, 
    Button, 
    LoadingIndicator,
    DateRangePicker
  } from 'frappe-ui'
  import CheckIcon from '@/components/Icons/CheckIcon.vue'
  import DeclinedCallIcon from '@/components/Icons/DeclinedCallIcon.vue'
  
  const scheduledCallsResource = createResource({
    url: 'crm.api.contact.get_scheduled_calls',
    method: 'GET',
    params: {
      today_only: true
    },
    cache: ['Scheduled Calls'],
    auto: true
  })
  
  const rows = computed(() => {
    return scheduledCallsResource.data || []
  })
  
  const filters = ref({
    date_range: {
      label: 'Date Range',
      type: 'Date',
      value: 'today'
    }
  })
  
  const updateDateFilter = () => {
    scheduledCallsResource.params.today_only = filters.value.date_range.value === 'today'
    scheduledCallsResource.reload()
  }
  
  const markCallStatusResource = createResource({
    url: 'crm.api.contact.mark_call_status',
    method: 'POST',
    onSuccess: (response) => {
      scheduledCallsResource.reload()
    },
    onError: (error) => {
      console.error('Error marking call status:', error)
    }
  })
  
  const markCallStatus = (row, status) => {
    markCallStatusResource.submit({
      contact: row.name,
      status: status
    })
  }
  
  const handleRealtimeUpdate = () => {
    scheduledCallsResource.reload()
  }
  
  onMounted(() => {
    frappe.realtime.on('scheduled_call_updated', handleRealtimeUpdate)
  })
  
  onUnmounted(() => {
    frappe.realtime.off('scheduled_call_updated', handleRealtimeUpdate)
  })
  </script>