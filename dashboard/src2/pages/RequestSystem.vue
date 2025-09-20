<template>
	<div class="p-4">
		<ObjectList :options="requestSystemOptions" />
	</div>
</template>

<script>
import ObjectList from '../components/ObjectList.vue';

export default {
	name: 'RequestSystem',
	components: {
		ObjectList,
	},
	data() {
		return {};
	},
	computed: {
		requestSystemOptions() {
			return {
				resource() {
					return {
						url: 'press.api.mbw_notification_request.get_mbw_notification_requests',
						transform(data) {
							return data.map((d) => ({
								site: d.site,
								status: d.status,
								type: d.type,
								creation: d.creation,
								description: d.description,
								name: d.name,
							}));
						},
						initialData: [],
						auto: true,
					};
				},
				updateFilters(filters) {
					// Update the resource with new filter parameters
					const params = {};
					if (filters.status) params.status = filters.status;
					if (filters.type) params.type = filters.type;
					if (filters.site) params.site = filters.site;
					
					this.$resources.list.update({ params });
					this.$resources.list.reload();
				},
				filterControls() {
					return [
						{
							type: 'select',
							label: 'Status',
							fieldname: 'status',
							options: [
								{ label: '', value: '' },
								{ label: 'Ongoing', value: 'Ongoing' },
								{ label: 'Done', value: 'Done' },
							],
						},
						{
							type: 'select',
							label: 'Type',
							fieldname: 'type',
							options: [
								{ label: '', value: '' },
								{ label: 'Restore', value: 'Restore' },
								{ label: 'Drop site', value: 'Drop site' },
								{ label: 'Deactivate site', value: 'Deactivate site' },
							],
						},
					];
				},
				columns: [
					{
						label: 'Site',
						fieldname: 'site',
						width: '200px',
					},
					{
						label: 'Status',
						fieldname: 'status',
						width: '120px',
						type: 'Badge',
						format(value) {
							return value || '';
						},
						theme(value) {
							if (value === 'Done') return 'green';
							if (value === 'Ongoing') return 'orange';
							return 'gray';
						},
						variant: 'solid',
					},
					{
						label: 'Type',
						fieldname: 'type',
						width: '150px',
						type: 'Badge',
						format(value) {
							return value || '';
						},
						theme(value) {
							const typeColors = {
								'Restore': 'blue',
								'Drop site': 'red',
								'Deactivate site': 'orange'
							};
							return typeColors[value] || 'gray';
						},
						variant: 'solid',
					},
					{
						label: 'Description',
						fieldname: 'description',
						width: '450px',
						format(value) {
							if (!value) return '';
							try {
								const div = document.createElement('div');
								div.innerHTML = String(value);
								return div.textContent || div.innerText || '';
							} catch (e) {
								return String(value).replace(/<[^>]*>/g, '');
							}
						},
					},
					{
						label: 'Create Time',
						fieldname: 'creation',
						width: '180px',
						format(value) {
							if (!value) return '';
							const date = new Date(value);
							return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
						},
					},
				],
				onRowClick(row) {
					console.log('Request clicked:', row);
					// You can add navigation to detail view here if needed
				},
			};
		},
	},
};
</script>
