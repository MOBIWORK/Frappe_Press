<template>
	<Card
		:title="$t('Site_Info')"
		:subtitle="$t('General_information_about_your_site')"
	>
		<div class="divide-y">
			<div class="flex items-center py-3">
				<Avatar
					v-if="info.owner"
					:image="info.owner.user_image"
					:label="info.owner.first_name"
				/>
				<div class="ml-3 flex flex-1 items-center justify-between">
					<div>
						<div class="text-base text-gray-600">{{ $t('Owned_By') }}</div>
						<div class="text-base font-medium text-gray-900">
							{{ info.owner.first_name }}
							{{ info.owner.last_name }}
						</div>
					</div>
					<div class="text-right">
						<div class="text-base text-gray-600">{{ $t('Created_On') }}</div>
						<div class="text-base font-medium text-gray-900">
							{{ $date(info.created_on).toFormat('dd-MM-yyyy') }}
						</div>
					</div>
					<div v-if="info.last_deployed" class="text-right">
						<div class="text-base text-gray-600">{{ $t('Last_Deployed') }}</div>
						<div class="text-base font-medium text-gray-900">
							{{ $date(info.last_deployed).toFormat('dd-MM-yyyy') }}
						</div>
					</div>
				</div>
			</div>

			<ListItem
				v-if="site.group && site.status !== 'Pending'"
				:title="$t('Auto_Update_Site')"
				class="overflow-x-hidden"
				:description="$t('SiteOverviewInfo_content_1')"
			>
				<template v-slot:actions>
					<LoadingIndicator class="h-4 w-4" v-if="loading" />
					<input
						v-show="!loading"
						id="auto-update-checkbox"
						@input="changeAutoUpdateSettings"
						type="checkbox"
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
				</template>
			</ListItem>
			<ListItem
				v-if="site.status == 'Active'"
				:title="$t('Deactivate_Site')"
				:description="$t('SiteOverviewInfo_content_2')"
			>
				<template v-slot:actions>
					<Tooltip
						:text="
							!permissions.deactivate
								? $t('SiteOverviewPlan_content_3')
								: $t('Deactivate_Site')
						"
					>
						<Button
							@click="onDeactivateClick"
							class="shrink-0"
							:disabled="!permissions.deactivate"
						>
							{{ $t('btn_Deactivate_Site') }}
						</Button>
					</Tooltip>
				</template>
			</ListItem>

			<ListItem
				v-if="['Inactive', 'Broken'].includes(site.status)"
				:title="$t('Activate_Site')"
				:description="$t('SiteOverviewInfo_content_3')"
			>
				<template v-slot:actions>
					<Button
						@click="onActivateClick"
						class="shrink-0"
						:variant="site.status === 'Broken' ? 'solid' : 'subtle'"
					>
						{{ $t('Activate_Site') }}
					</Button>
				</template>
			</ListItem>

			<ListItem
				v-if="site.status !== 'Pending'"
				:title="$t('Drop_Site')"
				:description="$t('SiteOverviewInfo_content_4')"
			>
				<template v-slot:actions>
					<SiteDrop :site="site" v-slot="{ showDialog }">
						<Tooltip
							:text="
								!permissions.drop
									? $t('SiteOverviewPlan_content_3')
									: $t('Drop_Site')
							"
						>
							<Button
								theme="red"
								:disabled="!permissions.drop"
								@click="showDialog"
							>
								{{ $t('Drop_Site') }}
							</Button>
						</Tooltip>
					</SiteDrop>
				</template>
			</ListItem>
		</div>
	</Card>
</template>
<script>
import SiteDrop from './SiteDrop.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'SiteOverviewInfo',
	props: ['site', 'info'],
	components: { SiteDrop },
	data() {
		return {
			loading: false
		};
	},
	mounted() {
		const autoUpdateCheckbox = document.getElementById('auto-update-checkbox');

		if (autoUpdateCheckbox) {
			autoUpdateCheckbox.checked = this.info.auto_updates_enabled;
		}
	},
	methods: {
		changeAutoUpdateSettings(event) {
			event.preventDefault();
			this.loading = true;

			return this.$call('press.api.site.change_auto_update', {
				name: this.site.name,
				auto_update_enabled: event.target.checked
			}).then(() => {
				setTimeout(() => window.location.reload(), 1000);
			});
		},
		onDeactivateClick() {
			this.$confirm({
				title: this.$t('Deactivate_Site'),
				message: this.$t('SiteOverviewInfo_content_5'),
				actionLabel: this.$t('Deactivate'),
				actionColor: 'red',
				action: () => this.deactivate()
			});
		},
		onActivateClick() {
			this.$confirm({
				title: this.$t('Activate_Site'),
				message: this.$t('SiteOverviewInfo_content_6'),
				actionLabel: this.$t('Activate'),
				action: () => this.activate()
			});
		},
		deactivate() {
			return this.$call('press.api.site.deactivate', {
				name: this.site.name
			}).then(() => {
				setTimeout(() => window.location.reload(), 1000);
			});
		},
		activate() {
			this.$call('press.api.site.activate', {
				name: this.site.name
			});
			notify({
				title: this.$t('Site_content_3'),
				message: this.$t('Site_content_4'),
				icon: 'check',
				color: 'green'
			});
			setTimeout(() => window.location.reload(), 1000);
		}
	},
	computed: {
		permissions() {
			return {
				drop: this.$account.hasPermission(
					this.site.name,
					'press.api.site.archive'
				),
				deactivate: this.$account.hasPermission(
					this.site.name,
					'press.api.site.deactivate'
				)
			};
		}
	}
};
</script>
