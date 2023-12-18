<template>
	<Dialog
		v-model="show"
		@close="resetValues"
		:options="{ title: 'Nâng cấp phiên bản trang web' }"
	>
		<template #body-content>
			<div class="space-y-4">
				<p v-if="site?.is_public && nextVersion" class="text-base">
					Trang web <b>{{ site.host_name }}</b> sẽ được nâng cấp lên
					<b>{{ nextVersion }}</b>
				</p>
				<FormControl
					v-else-if="privateReleaseGroups.length > 0 && nextVersion"
					:label="`Vui lòng chọn một bench ${nextVersion} để nâng cấp trang web từ ${site.frappe_version}`"
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
					label="Lên lịch di chuyển trang web"
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
				label="Thêm server vào bench"
				@click="$resources.addServerToReleaseGroup.submit()"
				:loading="
					$resources.addServerToReleaseGroup.loading ||
					$resources.validateGroupforUpgrade.loading
				"
			/>
			<Button
				class="w-full"
				variant="solid"
				label="Nâng cấp"
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
				return 'Trang web này đã ở trên phiên bản mới nhất.';
			} else if (!this.privateReleaseGroup) {
				return '';
			} else if (!this.site.is_public && !this.privateReleaseGroups.length)
				return `Nhóm của bạn không sở hữu bất kỳ bench riêng nào có sẵn để nâng cấp trang web này lên ${this.nextVersion}.`;
			else if (!this.site.is_public && !this.benchHasCommonServer)
				return `Bench đã chọn và trang web của bạn không có server chung. Vui lòng thêm server của trang web vào bench.`;
			else if (!this.site.is_public && this.benchHasCommonServer)
				return `Bench đã chọn và trang web của bạn có server chung. Bạn có thể tiếp tục với việc nâng cấp lên ${this.nextVersion}.`;
			else return '';
		},
		datetimeInIST() {
			if (!this.targetDateTime) return null;
			const datetimeInIST = this.$dayjs(this.targetDateTime)
				.tz('Asia/Kolkata')
				.format('YYYY-MM-DDTHH:mm');

			return datetimeInIST;
		}
	},
	resources: {
		versionUpgrade() {
			return {
				url: 'press.api.site.version_upgrade',
				params: {
					name: this.site?.name,
					destination_group: this.privateReleaseGroup,
					scheduled_datetime: this.datetimeInIST
				},
				onSuccess() {
					notify({
						title: 'Nâng cấp phiên bản trang web',
						message: `Lên lịch nâng cấp trang web cho <b>${this.site?.host_name}</b> đến <b>${this.nextVersion}</b>`,
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
						title: 'Server đã được thêm vào Bench',
						message: `Đã thêm một server vào bench <b>${this.privateReleaseGroup}</b>. Vui lòng đợi cho đến khi bench hoàn tất việc triển khai.`,
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
