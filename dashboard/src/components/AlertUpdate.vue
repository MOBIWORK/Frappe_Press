<template>
	<Alert :title="alertTitle" v-if="show">
		<span v-if="deployInformation.deploy_in_progress"
			>Quá trình triển khai cho bench này đang được tiến hành</span
		>
		<span v-else-if="bench.status == 'Active'">
			Có bản cập nhật mới cho bench của bạn. Bạn có muốn triển khai cập nhật
			ngay bây giờ không?
		</span>
		<span v-else>
			Bench của bạn chưa được triển khai. Bạn có thể thêm nhiều ứng dụng khác
			vào bench trước khi triển khai. Nếu bạn muốn triển khai ngay bây giờ, hãy
			nhấp vào nút `Hiển thị cập nhật`.
		</span>
		<template #actions>
			<Button
				v-if="deployInformation.deploy_in_progress"
				variant="solid"
				:route="`/benches/${bench.name}/deploys/${deployInformation.last_deploy.name}`"
				>Xem tiến trình</Button
			>
			<Button
				v-else
				variant="solid"
				@click="
					() => {
						showDeployDialog = true;
						step = 'Apps';
					}
				"
			>
				Hiển thị cập nhật
			</Button>
		</template>

		<Dialog
			:options="{
				title:
					step == 'Apps'
						? 'Chọn các ứng dụng bạn muốn cập nhật'
						: 'Chọn các tổ chức bạn muốn cập nhật'
			}"
			v-model="showDeployDialog"
		>
			<template v-slot:body-content>
				<BenchAppUpdates
					v-if="step == 'Apps'"
					:apps="deployInformation.apps"
					v-model:selectedApps="selectedApps"
					:removedApps="deployInformation.removed_apps"
				/>
				<BenchSiteUpdates
					class="p-1"
					v-if="step == 'Sites'"
					:sites="deployInformation.sites"
					v-model:selectedSites="selectedSites"
				/>
				<ErrorMessage class="mt-2" :message="errorMessage" />
			</template>
			<template v-slot:actions>
				<Button v-if="step == 'Sites'" class="w-full" @click="step = 'Apps'">
					Quay lại
				</Button>
				<Button
					v-if="step == 'Sites'"
					variant="solid"
					class="mt-2 w-full"
					@click="$resources.deploy.submit()"
					:loading="$resources.deploy.loading"
				>
					{{ selectedSites.length > 0 ? 'Cập nhật' : 'Bỏ qua và Triển khai' }}
				</Button>
				<Button v-else variant="solid" class="w-full" @click="step = 'Sites'">
					Tiếp theo
				</Button>
			</template>
		</Dialog>
	</Alert>
</template>
<script>
import BenchAppUpdates from './BenchAppUpdates.vue';
import BenchSiteUpdates from './BenchSiteUpdates.vue';
import SwitchTeamDialog from './SwitchTeamDialog.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AlertBenchUpdate',
	props: ['bench'],
	components: {
		BenchAppUpdates,
		BenchSiteUpdates,
		SwitchTeamDialog
	},
	data() {
		return {
			showDeployDialog: false,
			showTeamSwitcher: false,
			selectedApps: [],
			selectedSites: [],
			step: 'Apps'
		};
	},
	resources: {
		deployInformation() {
			return {
				url: 'press.api.bench.deploy_information',
				params: {
					name: this.bench?.name
				},
				auto: true
			};
		},
		deploy() {
			return {
				url: 'press.api.bench.deploy_and_update',
				params: {
					name: this.bench?.name,
					apps: this.selectedApps,
					sites: this.selectedSites
				},
				validate() {
					if (
						this.selectedApps.length === 0 &&
						this.deployInformation.removed_apps.length === 0
					) {
						return 'Bạn phải chọn ít nhất 1 ứng dụng để tiếp tục cập nhật.';
					}
				},
				onSuccess(new_candidate_name) {
					this.showDeployDialog = false;
					this.$resources.deployInformation.setData({
						...this.$resources.deployInformation.data,
						deploy_in_progress: true,
						last_deploy: { name: new_candidate_name, status: 'Running' }
					});
					notify({
						title: 'Cập nhật đã được lên lịch thành công',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	},
	computed: {
		show() {
			if (this.deployInformation) {
				return (
					this.deployInformation.update_available &&
					['Awaiting Deploy', 'Active'].includes(this.bench.status)
				);
			}
		},
		errorMessage() {
			return (
				this.$resources.deploy.error ||
				(this.bench.team !== $account.team.name
					? 'Nhóm hiện tại không có đủ quyền hạn'
					: '')
			);
		},
		deployInformation() {
			return this.$resources.deployInformation.data;
		},
		alertTitle() {
			if (this.deployInformation && this.deployInformation.deploy_in_progress) {
				return 'Triển khai đang được tiến hành';
			}
			return this.bench.status == 'Active' ? 'Update Available' : 'Deploy';
		}
	}
};
</script>
