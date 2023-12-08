<template>
	<Alert :title="alertTitle" v-if="show">
		<span v-if="deployInformation.deploy_in_progress"
			>Một quá trình triển khai cho bench này đang trong quá trình tiến
			hành.</span
		>
		<span v-else-if="bench.status == 'Active'">
			Cập nhật mới đã sẵn có cho bench của bạn. Bạn có muốn triển khai cập nhật
			ngay bây giờ không?
		</span>
		<span v-else>
			Bench của bạn chưa được triển khai. Bạn có thể thêm nhiều ứng dụng khác
			vào bench trước khi triển khai. Nếu bạn muốn triển khai ngay bây giờ, hãy
			nhấp vào "Triển khai".
		</span>
		<template #actions>
			<Button
				v-if="deployInformation.deploy_in_progress"
				variant="solid"
				:route="`/benches/${bench.name}/deploys/${deployInformation.last_deploy.name}`"
				>Xem tiến trình</Button
			>
			<Tooltip
				v-else
				:text="
					!permissions.update
						? `Bạn không có đủ quyền để thực hiện hành động này`
						: ''
				"
			>
				<Button
					variant="solid"
					:disabled="!permissions.update"
					@click="showDeployDialog = true"
				>
					Hiển thị cập nhật
				</Button>
			</Tooltip>
		</template>

		<Dialog
			:options="{ title: 'Chọn các ứng dụng mà bạn muốn cập nhật' }"
			v-model="showDeployDialog"
		>
			<template v-slot:body-content>
				<BenchAppUpdates
					:apps="deployInformation.apps"
					v-model:selectedApps="selectedApps"
					:removedApps="deployInformation.removed_apps"
				/>
				<ErrorMessage class="mt-2" :message="errorMessage" />
			</template>
			<template v-slot:actions>
				<Button
					class="w-full"
					variant="solid"
					@click="$resources.deploy.submit()"
					:loading="$resources.deploy.loading"
					v-if="this.bench.team === $account.team.name"
				>
					Triển khai
				</Button>
				<Button
					class="w-full"
					variant="solid"
					@click="showTeamSwitcher = true"
					v-else
				>
					Chuyển nhóm
				</Button>
				<SwitchTeamDialog v-model="showTeamSwitcher" />
			</template>
		</Dialog>
	</Alert>
</template>
<script>
import BenchAppUpdates from './BenchAppUpdates.vue';
import SwitchTeamDialog from './SwitchTeamDialog.vue';
export default {
	name: 'AlertBenchUpdate',
	props: ['bench'],
	components: {
		BenchAppUpdates,
		SwitchTeamDialog
	},
	data() {
		return {
			showDeployDialog: false,
			showTeamSwitcher: false,
			selectedApps: []
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
				url: 'press.api.bench.deploy',
				params: {
					name: this.bench?.name,
					apps: this.selectedApps
				},
				validate() {
					if (
						this.selectedApps.length === 0 &&
						this.deployInformation.removed_apps.length === 0
					) {
						return 'Bạn phải chọn ít nhất 1 ứng dụng để tiếp tục với quá trình cập nhật.';
					}
				},
				onSuccess(candidate) {
					this.$router.push(`/benches/${this.bench.name}/deploys/${candidate}`);
					this.showDeployDialog = false;
				}
			};
		}
	},
	computed: {
		permissions() {
			return {
				update: this.$account.hasPermission(
					this.bench.name,
					'press.api.bench.deploy_and_update'
				)
			};
		},
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
					? 'Nhóm hiện tại không có đủ quyền.'
					: '')
			);
		},
		deployInformation() {
			return this.$resources.deployInformation.data;
		},
		alertTitle() {
			if (this.deployInformation && this.deployInformation.deploy_in_progress) {
				return 'Quá trình triển khai đang được thực hiện.';
			}
			return this.bench.status == 'Active' ? 'Update Available' : 'Deploy';
		}
	}
};
</script>
