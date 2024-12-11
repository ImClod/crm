// @/utils/scheduledCall.js
import {
    secondsToDuration,
    dateFormat,
    dateTooltipFormat,
    timeAgo,
  } from '@/utils'
  import { usersStore } from '@/stores/users'
  import { contactsStore } from '@/stores/contacts'
  
  const { getUser } = usersStore()
  const { getContact, getLeadContact } = contactsStore()
  
  export function getScheduledCallDetail(row, scheduledCall) {
    // Implementa la logica di trasformazione dei dati
    // Simile a getCallLogDetail in callLog.js
    
    if (row === 'contact') {
      return {
        label: getContact(scheduledCall.contact)?.full_name || 'Unknown',
        image: getContact(scheduledCall.contact)?.image
      }
    } else if (row === 'date') {
      return {
        label: dateFormat(scheduledCall.date, dateTooltipFormat),
        timeAgo: timeAgo(scheduledCall.date)
      }
    } else if (row === 'status') {
      return {
        label: scheduledCall.status || 'Pending',
        color: getStatusColor(scheduledCall.status)
      }
    }
    
    // Per impostazione predefinita, restituisci il valore originale
    return scheduledCall[row]
  }
  
  function getStatusColor(status) {
    const statusColorMap = {
      'Completed': 'green',
      'Pending': 'gray',
      'Cancelled': 'red',
      'Scheduled': 'blue'
    }
    return statusColorMap[status] || 'gray'
  }