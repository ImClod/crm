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
        <Table>
          <template #header>
            <TableRow>
              <TableHeaderCell>{{ __('Name') }}</TableHeaderCell>
              <TableHeaderCell>{{ __('Email') }}</TableHeaderCell>
              <TableHeaderCell>{{ __('Mobile') }}</TableHeaderCell>
              <TableHeaderCell>{{ __('First Call Date') }}</TableHeaderCell>
              <TableHeaderCell>{{ __('Actions') }}</TableHeaderCell>
            </TableRow>
          </template>
          <template #body>
            <TableRow v-for="row in rows" :key="row.name">
              <TableCell>{{ row.full_name }}</TableCell>
              <TableCell>{{ row.email }}</TableCell>
              <TableCell>{{ row.mobile_no }}</TableCell>
              <TableCell>{{ row.custom_first_date }}</TableCell>
              <TableCell>
                <div class="flex items-center space-x-2">
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
              </TableCell>
            </TableRow>
          </template>
        </Table>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { 
    createResource, 
    Tooltip, 
    Button, 
    Table, 
    TableRow, 
    TableHeaderCell, 
    TableCell,
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