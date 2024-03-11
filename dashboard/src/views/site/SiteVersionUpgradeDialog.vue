<template>
	<Dialog
		v-model="show"
		@close="resetValues"
		:options="{ title: $t('upgrade_site_version') }"
	>
		<template #body-content>
			<div class="space-y-4">
				<p v-if="site?.is_public && nextVersion" class="text-base">
					{{ $t('the_site') }} <b>{{ site.host_name }}</b>
					{{ $t('will_be_upgraded_to') }}
					<b>{{ nextVersion }}</b>
				</p>
				<FormControl
					v-else-if="privateReleaseGroups.length > 0 && nextVersion"
					:label="`${$t(
						'SiteVersionUpgradeDialog_content_1'
					)} ${nextVersion} ${$t('SiteVersionUpgradeDialog_content_2')} ${
						site.frappe_version
					}`"
					class="w-full"
					type="select"
					:options="privateReleaseGroups"
					v-model="privateReleaseGroup"
					@change="
						value =>
							$resources.validateGroupforUpgrade.submit({
								name: site.name,
								group_name: value.target.value
							})
					"
				/>
				<FormControl
					class="mt-4"
					v-if="(site.is_public && nextVersion) || benchHasCommonServer"
					:label="$t('schedule_site_migration')"
					type="datetime-local"
					:min="new Date().toISOString().slice(0, 16)"
					v-model="targetDateTime"
				/>
				<p v-if="message" class="text-sm text-gray-700">
					{{ message }}
				</p>
				<ErrorMessage
					:message="
						$resources.versionUpgrade.error ||
						$resources.validateGroupforUpgrade.error ||
						$resources.addServerToReleaseGroup.error ||
						$resources.getPrivateGroups.error
					"
				/>
			</div>
		</template>
		<template v-if="site?.is_public || privateReleaseGroups.length" #actions>
			<Button
				v-if="!site.is_public"
				class="mb-2 w-full"
				:disabled="benchHasCommonServer || !privateReleaseGroup"
				:label="$t('add_server_to_bench')"
				@click="$resources.addServerToReleaseGroup.submit()"
				:loading="
					$resources.addServerToReleaseGroup.loading ||
					$resources.validateGroupforUpgrade.loading
				"
			/>
			<Button
				class="w-full"
				variant="solid"
				:label="$t('upgrade')"
				:disabled="
					(!benchHasCommonServer || !privateReleaseGroup) && !site.is_public
				"
				:loading="
					$resources.versionUpgrade.loading ||
					$resources.validateGroupforUpgrade.loading
				"
				@click="$resources.versionUpgrade.submit()"
			/>
		</template>
	</Dialog>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'SiteVersionUpgradeDialog',
	props: ['site', 'modelValue'],
	emits: ['update:modelValue'],
	data() {
		return {
			targetDateTime: null,
			privateReleaseGroup: '',
			benchHasCommonServer: false
		};
	},
	watch: {
		show(value) {
			if (value && !this.site?.is_public)
				this.$resources.getPrivateGroups.fetch();
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
		},
		nextVersion() {
			const nextNumber = Number(this.site?.frappe_version.split(' ')[1]);
			if (isNaN(nextNumber)) return null;

			return `Version ${nextNumber + 1}`;
		},
		privateReleaseGroups() {
			return this.$resources.getPrivateGroups.data;
		},
		message() {
			if (this.site.frappe_version === this.site.latest_frappe_version) {
				return this.$t('SiteVersionUpgradeDialog_content_3');
			} else if (!this.privateReleaseGroup) {
				return '';
			} else if (!this.site.is_public && !this.privateReleaseGroups.length)
				return `${this.$t('SiteVersionUpgradeDialog_content_4')} ${
					this.nextVersion
				}.`;
			else if (!this.site.is_public && !this.benchHasCommonServer)
				return this.$t('SiteVersionUpgradeDialog_content_5');
			else if (!this.site.is_public && this.benchHasCommonServer)
				return `${this.$t('SiteVersionUpgradeDialog_content_6')} ${
					this.nextVersion
				}.`;
			else return '';
		},
		datetimeInVN() {
			if (!this.targetDateTime) return null;
			const datetimeInVN = this.$dayjs(this.targetDateTime)
				.tz('Asia/Ho_Chi_Minh')
				.format('YYYY-MM-DDTHH:mm');

			return datetimeInVN;
		}
	},
	resources: {
		versionUpgrade() {
			return {
				url: 'press.api.site.version_upgrade',
				params: {
					name: this.site?.name,
					destination_group: this.privateReleaseGroup,
					scheduled_datetime: this.datetimeInVN,
					lang: this.$i18n.locale
				},
				onSuccess() {
					notify({
						title: $t('site_version_upgrade'),
						message: `${this.$t('SiteVersionUpgradeDialog_content_7')} <b>${
							this.site?.host_name
						}</b> ${this.$t('to')} <b>${this.nextVersion}</b>`,
						icon: 'check',
						color: 'green'
					});
					this.$emit('update:modelValue', false);
				}
			};
		},
		getPrivateGroups() {
			return {
				url: 'press.api.site.get_private_groups_for_upgrade',
				params: {
					name: this.site?.name,
					version: this.site?.frappe_version
				},
				transform(data) {
					return data.map(group => ({
						label: group.title || group.name,
						value: group.name
					}));
				},
				initialData: []
			};
		},
		addServerToReleaseGroup() {
			return {
				url: 'press.api.site.add_server_to_release_group',
				params: {
					name: this.site?.name,
					group_name: this.privateReleaseGroup
				},
				onSuccess(data) {
					notify({
						title: this.$t('server_added_to_the_bench'),
						message: `${this.$t('SiteVersionUpgradeDialog_content_8')} <b>${
							this.privateReleaseGroup
						}</b>. ${this.$t('SiteVersionUpgradeDialog_content_9')}`,
						icon: 'check',
						color: 'green'
					});
					this.$router.push({
						name: 'BenchJobs',
						params: {
							benchName: this.privateReleaseGroup,
							jobName: data
						}
					});
					this.resetValues();
					this.$emit('update:modelValue', false);
				}
			};
		},
		validateGroupforUpgrade() {
			return {
				url: 'press.api.site.validate_group_for_upgrade',
				onSuccess(data) {
					this.benchHasCommonServer = data;
				}
			};
		}
	},
	methods: {
		resetValues() {
			this.targetDateTime = null;
			this.privateReleaseGroup = '';
			this.benchHasCommonServer = false;
			this.$resources.getPrivateGroups.reset();
		}
	}
};
</script>
