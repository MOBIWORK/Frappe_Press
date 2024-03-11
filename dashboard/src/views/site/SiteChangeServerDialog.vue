<template>
	<Dialog
		v-model="show"
		@close="resetValues"
		:options="{
			title: $t('move_site_to_another_server'),
			actions: [
				{
					label: checkForBench
						? $t('check_for_available_benches')
						: $t('submit'),
					loading: $resources.changeServer.loading,
					variant: 'solid',
					disabled: !$resources.changeServerOptions?.data?.length,
					onClick: () => {
						if (checkForBench) {
							$resources.changeServerBenchOptions.fetch();
						} else {
							$resources.changeServer.submit({
								name: site?.name,
								group: targetBench,
								scheduled_datetime: targetDateTime
							});
						}
					}
				}
			]
		}"
	>
		<template #body-content>
			<LoadingIndicator
				class="mx-auto h-4 w-4"
				v-if="$resources.changeServerOptions.loading"
			/>
			<FormControl
				v-else-if="$resources.changeServerOptions.data.length > 0"
				:label="$t('select_server')"
				type="select"
				:options="$resources.changeServerOptions.data"
				v-model="targetServer"
			/>
			<p v-else class="text-base">
				{{ $t('SiteChangeServerDialog_content_1') }}
			</p>
			<FormControl
				class="mt-4"
				v-if="$resources.changeServerBenchOptions.data.length > 0"
				:label="$t('select_bench')"
				type="select"
				:options="$resources.changeServerBenchOptions.data"
				v-model="targetBench"
			/>
			<FormControl
				class="mt-4"
				v-if="$resources.changeServerBenchOptions.data.length > 0"
				:label="$t('schedule_site_migration')"
				type="datetime-local"
				:min="new Date().toISOString().slice(0, 16)"
				v-model="targetDateTime"
			/>
			<ErrorMessage
				class="mt-4"
				:message="
					$resources.changeServer.error ||
					$resources.changeServerBenchOptions.error
				"
			/>
		</template>
	</Dialog>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'SiteChangeServerDialog',
	props: ['site', 'modelValue'],
	emits: ['update:modelValue'],
	data() {
		return {
			targetBench: '',
			targetServer: '',
			targetDateTime: null,
			checkForBench: true
		};
	},
	watch: {
		show(value) {
			if (value) this.$resources.changeServerOptions.fetch();
		}
	},
	computed: {
		show: {
			get() {
				return this.modelValue;
			},
			set(value) {
				this.$emit('update:modelValue', value);
			}
		}
	},
	resources: {
		changeServerOptions() {
			return {
				url: 'press.api.site.change_server_options',
				params: {
					name: this.site?.name
				},
				transform(d) {
					return d.map(s => ({
						label: s.title || s.name,
						value: s.name
					}));
				},
				onSuccess(data) {
					if (data.length > 0) this.targetServer = data[0].name;
				}
			};
		},
		changeServerBenchOptions() {
			return {
				url: 'press.api.site.change_server_bench_options',
				params: {
					name: this.site?.name,
					server: this.targetServer,
					lang: this.$i18n.locale
				},
				initialData: [],
				transform(d) {
					return d.map(s => ({
						label: s.title || s.name,
						value: s.name
					}));
				},
				onSuccess(data) {
					this.targetBench = data[0].name;
					this.checkForBench = false;
				}
			};
		},
		changeServer() {
			return {
				url: 'press.api.site.change_server',
				onSuccess() {
					notify({
						title: this.$t('site_change_server'),
						message: `${this.$t('site')} <b>${this.site?.name}</b> ${this.$t(
							'SiteChangeServerDialog_content_2'
						)} <b>${this.targetServer}</b>`,
						icon: 'check',
						color: 'green'
					});
					this.$emit('update:modelValue', false);
				}
			};
		}
	},
	methods: {
		resetValues() {
			this.targetBench = '';
			this.targetServer = '';
			this.targetDateTime = null;
			this.checkForBench = true;
		}
	}
};
</script>
