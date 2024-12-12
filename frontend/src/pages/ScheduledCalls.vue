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
          <tr v-for="row in rows" :key="row.name">
            <td class="px-6 py-4 whitespace-nowrap">{{ row.full_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ row.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ row.mobile_no }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ row.status }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="confirmCall(row)" class="text-green-600 hover:text-green-900">Conferma</button>
              <button @click="rejectCall(row)" class="text-red-600 hover:text-red-900 ml-4">Rifiuta</button>
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
import { createResource } from 'frappe-ui';
import { computed } from 'vue';

export default {
  setup() {
    const resource = createResource({
      url: '/api/contact/get_scheduled_calls',
      auto: true,
    });

    const rows = computed(() => {
      if (!resource.data) return [];
      return resource.data.map(item => ({
          ...item,
      }));
    });

    const markCallStatus = async (contact, status) => {
      try {
        const response = await fetch('/api/contact/mark_call_status', { // Assicurati di inserire il percorso corretto dell'API
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            contact: contact.name, // Assicurati che 'name' sia l'identificativo univoco del contatto
            status: status
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Errore durante l\'aggiornamento dello stato della chiamata.'); // Gestione più dettagliata degli errori
        }

        // Aggiorna la lista delle chiamate dopo l'aggiornamento dello stato
        resource.refresh()

        console.log('Stato chiamata aggiornato con successo.');
      } catch (error) {
        console.error('Errore durante l\'aggiornamento dello stato della chiamata:', error);
        // Qui puoi mostrare un messaggio di errore all'utente, ad esempio con un alert o un toast
        alert("errore durante l'aggiornamento")
      }
    };


    const confirmCall = async (row) => {
      console.log('Conferma chiamata per:', row.full_name);
      await markCallStatus(row, 'Confirmed');
    };

    const rejectCall = async (row) => {
      console.log('Rifiuta chiamata per:', row.full_name);
      await markCallStatus(row, 'Canceled');
    };

    return { resource, rows, confirmCall, rejectCall };
  },
};
</script>

<style>
/* Aggiungi qui i tuoi stili CSS personalizzati */
</style>