<template>
    <Dialog v-model="show">
      <template #body-title>
        <div class="flex items-center gap-3">
          <h3 class="text-2xl font-semibold leading-6 text-gray-900">
            {{ __('Scheduled Call Details') }}
          </h3>
        </div>
      </template>
      <template #body-content>
        <div class="flex flex-col gap-3.5">
          <div
            v-for="field in detailFields"
            :key="field.name"
            class="flex gap-2 text-base text-gray-800"
          >
            <div class="grid size-7 place-content-center">
              <component :is="field.icon" />
            </div>
            <div class="flex min-h-7 w-full items-center gap-2">
              <div v-if="field.name === 'contact'" class="flex items-center gap-1">
                <Avatar
                  :image="field.value.image"
                  :label="field.value.label"
                  size="sm"
                />
                <div class="ml-1 flex flex-col gap-1">
                  {{ field.value.label }}
                </div>
              </div>
              <Tooltip v-else-if="field.tooltip" :text="field.tooltip">
                {{ field.value }}
              </Tooltip>
              <div 
                v-else 
                :class="field.color ? `text-${field.color}-600` : ''"
              >
                {{ field.value }}
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import { 
    FeatherIcon, 
    Avatar, 
    Tooltip, 
    createDocumentResource 
  } from 'frappe-ui'
  import { ref, computed, h, watch } from 'vue'
  import { useRouter } from 'vue-router'
  
  import CalendarIcon from '@/components/Icons/CalendarIcon.vue'
  import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
  import UserIcon from '@/components/Icons/UserIcon.vue'
  import CheckCircleIcon from '@/components/Icons/CheckCircleIcon.vue'
  
  const props = defineProps({
    name: {
      type: String,
      default: '',
    },
  })
  
  const show = defineModel()
  const router = useRouter()
  const scheduledCall = ref({})
  
  const detailFields = computed(() => {
    if (!scheduledCall.value.doc) return []
    
    let details = [
      {
        icon: ContactsIcon,
        name: 'contact',
        value: {
          label: scheduledCall.value.doc.contact_name,
          image: scheduledCall.value.doc.contact_image
        }
      },
      {
        icon: CalendarIcon,
        name: 'date',
        value: scheduledCall.value.doc.date,
        tooltip: scheduledCall.value.doc.date_formatted
      },
      {
        icon: UserIcon,
        name: 'owner',
        value: scheduledCall.value.doc.owner_name
      },
      {
        icon: CheckCircleIcon,
        name: 'status',
        value: scheduledCall.value.doc.status,
        color: scheduledCall.value.doc.status_color
      }
    ]
  
    return details.filter(detail => detail.value)
  })
  
  watch(show, (val) => {
    if (val) {
      scheduledCall.value = createDocumentResource({
        doctype: 'CRM Scheduled Call',
        name: props.name,
        fields: [
          'name', 
          'contact', 
          'contact_name', 
          'contact_image', 
          'date', 
          'status', 
          'owner',
          'notes'
        ],
        cache: ['scheduled_call', props.name],
        auto: true,
        transform: (doc) => {
          // Aggiungi qui eventuali trasformazioni dei dati
          return doc
        }
      })
    }
  })
  </script>