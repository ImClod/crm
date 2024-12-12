<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-bold mb-4">Chiamate Programmate</h2>

    <div v-if="resource.loading">
      <p>Caricamento dati...</p>
    </div>
    <div v-else-if="resource.error">
      <p>Errore durante il caricamento dei dati: {{ resource.error.message }}</p>
    </div>
    <div v-else-if="rows.length > 0">
      <table class="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Numero Mobile</th>
            <th class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stato</th>
            <th class="px-6 py-3 bg-gray-50"></th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="row in rows" :key="row.name" @click="goToContact(row)">
            <td class="px-6 py-4 whitespace-nowrap cursor-pointer">{{ row.full_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ row.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ row.mobile_no }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ row.custom_first_date }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click.stop="confirmCall(row)" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Conferma</button>
              <button @click.stop="rejectCall(row)" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-4">Rifiuta</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="!resource.loading && !resource.error">
      <p>Nessuna chiamata programmata trovata.</p>
    </div>
  </div>
</template>

<script>
import { createResource, call } from 'frappe-ui';
import { computed } from 'vue';


export default {
  setup() {
    const resource = createResource({
      url: 'crm.api.contact.get_scheduled_calls',
      auto: true,
    });
    console.log(resource.data)
    const rows = computed(() => {
      if (!resource.data) return [];
      return resource.data.map(item => ({
        ...item,
      }));
    });

    const goToContact = (row) => {
      // Redireziona alla scheda del contatto
      window.location.href = `/crm/contacts/${row.full_name}`; 
    };

    const markCallStatus = async (contact, status) => {
      try {
        await call('crm.api.contact.mark_call_status', {
          contact: contact.full_name,
          status: status,
        });
        resource.data = null;
        // Aggiorna la lista delle chiamate dopo l'aggiornamento dello stato
        resource.reload();
        console.log('Stato chiamata aggiornato con successo.');
      } catch (error) {
        console.error('Errore durante l\'aggiornamento dello stato della chiamata:', error);
        // Qui puoi mostrare un messaggio di errore all'utente, ad esempio con un alert o un toast
        alert("Errore durante l'aggiornamento");
      }
    };

    const confirmCall = async (row) => {
      console.log('Conferma chiamata per:', row.full_name);
      await markCallStatus(row, 'Completed');
    };

    const rejectCall = async (row) => {
      console.log('Rifiuta chiamata per:', row.full_name);
      await markCallStatus(row, 'Canceled');
    };

    return { resource, rows, confirmCall, rejectCall, goToContact };
  },
};
</script>

<style>
/* Aggiungi qui i tuoi stili CSS personalizzati */
</style>