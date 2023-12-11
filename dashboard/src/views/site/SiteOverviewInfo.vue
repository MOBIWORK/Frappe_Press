<template>
	<Card
		title="Thông tin trang web"
		subtitle="Thông tin chung về trang web của bạn"
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
						<div class="text-base text-gray-600">Sở hữu bởi</div>
						<div class="text-base font-medium text-gray-900">
							{{ info.owner.first_name }}
							{{ info.owner.last_name }}
						</div>
					</div>
					<div class="text-right">
						<div class="text-base text-gray-600">Ngày tạo</div>
						<div class="text-base font-medium text-gray-900">
							{{ $date(info.created_on).toFormat('dd-MM-yyyy') }}
						</div>
					</div>
					<div v-if="info.last_deployed" class="text-right">
						<div class="text-base text-gray-600">Lần triển khai cuối cùng</div>

						<div class="text-base font-medium text-gray-900">
							{{
								$date(info.last_deployed).toLocaleString({
									month: 'long',
									day: 'numeric'
								})
							}}
						</div>
					</div>
				</div>
			</div>

			<ListItem
				v-if="site.group && site.status !== 'Pending'"
				title="Tự động cập nhật trang web"
				class="overflow-x-hidden"
				description="Lên lịch tự động cập nhật trang web khi có sẵn"
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
				title="Ngưng hoạt động trang web"
				description="Trang web sẽ trở thành không hoạt động và sẽ không thể truy cập công khai"
			>
				<template v-slot:actions>
					<Tooltip
						:text="
							!permissions.deactivate
								? `Bạn không có đủ quyền để thực hiện hành động này`
								: 'Ngưng hoạt động trang web'
						"
					>
						<Button
							@click="onDeactivateClick"
							class="shrink-0"
							:disabled="!permissions.deactivate"
						>
							Ngưng hoạt động
						</Button>
					</Tooltip>
				</template>
			</ListItem>

			<ListItem
				v-if="['Inactive', 'Broken'].includes(site.status)"
				title="Kích hoạt trang web"
				description="Trang web sẽ trở nên hoạt động và có thể truy cập được"
			>
				<template v-slot:actions>
					<Button
						@click="onActivateClick"
						class="shrink-0"
						:variant="site.status === 'Broken' ? 'solid' : 'subtle'"
					>
						Kích hoạt trang web
					</Button>
				</template>
			</ListItem>

			<ListItem
				v-if="site.status !== 'Pending'"
				title="Xóa trang web"
				description="Một khi bạn xóa trang web, không có cách nào quay lại"
			>
				<template v-slot:actions>
					<SiteDrop :site="site" v-slot="{ showDialog }">
						<Tooltip
							:text="
								!permissions.drop
									? `Bạn không có đủ quyền để thực hiện hành động này`
									: 'Xóa trang web'
							"
						>
							<Button
								theme="red"
								:disabled="!permissions.drop"
								@click="showDialog"
							>
								Xóa trang web
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
				title: 'Ngưng hoạt động trang web',
				message: `
				Bạn có chắc chắn muốn ngưng hoạt động trang web này không? Trang web sẽ chuyển sang trạng thái không hoạt động. Nó sẽ không thể truy cập và các công việc nền sẽ không chạy. Bạn vẫn sẽ bị tính phí <strong>kể cả khi tắt</strong>.
				`,
				actionLabel: 'Ngưng hoạt động',
				actionColor: 'red',
				action: () => this.deactivate()
			});
		},
		onActivateClick() {
			this.$confirm({
				title: 'Kích hoạt trang web',
				message: `Bạn có chắc chắn muốn kích hoạt trang web này không?
<br><br><strong>Ghi chú: Sử dụng điều này như một phương án cuối cùng nếu trang web gặp sự cố và không thể truy cập được.</strong>`,
				actionLabel: 'Kích hoạt',
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
				title: 'Trang web đã được kích hoạt thành công!',
				message: 'Bạn có thể truy cập trang web của mình ngay bây giờ',
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
