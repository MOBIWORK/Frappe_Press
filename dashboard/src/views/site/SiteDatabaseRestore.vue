<template>
	<Card
		v-if="site"
		title="Khôi phục, Di chuyển và Đặt lại"
		:subtitle="
			site.status === 'Suspended'
				? 'Kích hoạt tổ chức để kích hoạt những hành động này'
				: ''
		"
	>
		<div class="divide-y">
			<div class="flex items-center justify-between py-3">
				<div>
					<h3 class="text-lg">Khôi phục</h3>
					<p class="mt-1 text-base text-gray-600">
						Khôi phục cơ sở dữ liệu của bạn bằng cách sử dụng một bản sao lưu
						trước đó
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.restore
							? `Bạn không có đủ quyền để thực hiện hành động này`
							: 'Khôi phục Database'
					"
				>
					<Button
						theme="red"
						:disabled="site.status === 'Suspended' || !permissions.restore"
						@click="showRestoreDialog = true"
					>
						Khôi phục
					</Button>
				</Tooltip>
			</div>
			<div class="flex items-center justify-between py-3">
				<div>
					<h3 class="text-lg">Migrate</h3>
					<p class="mt-1 text-base text-gray-600">
						Chạy lệnh `bench migrate` trên database của bạn.
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.migrate
							? `Bạn không có đủ quyền để thực hiện hành động này`
							: 'Migrate Database'
					"
				>
					<Button
						:disabled="site.status === 'Suspended' || !permissions.migrate"
						@click="showMigrateDialog = true"
					>
						Migrate
					</Button>
				</Tooltip>
			</div>
			<div class="flex items-center justify-between py-3">
				<div>
					<h3 class="text-lg">Đặt lại</h3>
					<p class="mt-1 text-base text-gray-600">
						Đặt lại database của bạn về trạng thái sạch sẽ.
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.reset
							? `Bạn không có đủ quyền để thực hiện hành động này`
							: 'Đặt lại Database'
					"
				>
					<Button
						theme="red"
						:disabled="site.status === 'Suspended' || !permissions.reset"
						@click="showResetDialog = true"
					>
						Đặt lại
					</Button>
				</Tooltip>
			</div>
			<div class="flex items-center justify-between py-3">
				<div>
					<h3 class="text-lg">Xóa Cache</h3>
					<p class="mt-1 text-base text-gray-600">
						Xóa bộ nhớ cache của tổ chức của bạn
					</p>
				</div>
				<Button
					:disabled="site.status === 'Suspended'"
					@click="confirmClearCache"
				>
					Xóa
				</Button>
			</div>
			<div
				class="flex items-center justify-between py-3"
				v-if="$account.team.database_access_enabled"
			>
				<div>
					<h3 class="text-lg">Truy cập</h3>
					<p class="mt-1 text-base text-gray-600">
						Kết nối vào database của bạn
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.access
							? `Bạn không có đủ quyền để thực hiện hành động này`
							: 'Truy cập Database'
					"
				>
					<Button
						:disabled="!permissions.access"
						icon-left="database"
						@click="showDatabaseAccessDialog = true"
					>
						Truy cập</Button
					>
				</Tooltip>
			</div>
		</div>

		<Dialog
			:options="{
				title: 'Migrate Database',
				actions: [
					{
						label: 'Migrate',
						variant: 'solid',
						theme: 'red',
						loading: $resources.migrateDatabase.loading,
						onClick: migrateDatabase
					}
				]
			}"
			v-model="showMigrateDialog"
			@close="
				() => {
					$resources.migrateDatabase.reset();
					wantToSkipFailingPatches = false;
				}
			"
		>
			<template v-slot:body-content>
				<p class="text-base">
					Lệnh <b>bench migrate</b> sẽ được thực hiện trên database của bạn. Bạn
					có chắc chắn muốn chạy lệnh này không? Chúng tôi khuyên bạn nên tải về
					một bản sao lưu database trước khi tiếp tục.
				</p>
				<ErrorMessage
					class="mt-2"
					:message="$resources.migrateDatabase.error"
				/>
				<div class="mt-2">
					<!-- Skip Failing Checkbox -->
					<input
						id="skip-failing"
						type="checkbox"
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						v-model="wantToSkipFailingPatches"
					/>
					<label for="skip-failing" class="ml-2 text-sm text-gray-900">
						Bỏ qua các bản vá (patch) không thành công (nếu có bất kỳ bản vá nào
						thất bại)
					</label>
				</div>
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: 'Khôi phục',
				actions: [
					{
						label: 'Khôi phục',
						variant: 'solid',
						loading: $resources.restoreBackup.loading,
						onClick: () => $resources.restoreBackup.submit()
					}
				]
			}"
			v-model="showRestoreDialog"
		>
			<template v-slot:body-content>
				<div class="space-y-4">
					<p class="text-base">
						Khôi phục database của bạn bằng cách sử dụng một bản sao lưu trước
						đó.
					</p>
					<BackupFilesUploader v-model:backupFiles="selectedFiles" />
				</div>
				<div class="mt-3">
					<!-- Skip Failing Checkbox -->
					<input
						id="skip-failing"
						type="checkbox"
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						v-model="wantToSkipFailingPatches"
					/>
					<label for="skip-failing" class="ml-2 text-sm text-gray-900">
						Bỏ qua các bản vá (patch) không thành công (nếu có bất kỳ bản vá nào
						thất bại)
					</label>
				</div>
				<ErrorMessage class="mt-2" :message="$resources.restoreBackup.error" />
			</template>
		</Dialog>

		<DatabaseAccessDialog
			v-if="showDatabaseAccessDialog"
			:site="site.name"
			v-model:show="showDatabaseAccessDialog"
		/>

		<Dialog
			:options="{
				title: 'Khôi phục Database',
				actions: [
					{
						label: 'Khôi phục',
						variant: 'solid',
						theme: 'red',
						loading: $resources.resetDatabase.loading,
						onClick: () => $resources.resetDatabase.submit()
					}
				]
			}"
			v-model="showResetDialog"
		>
			<template v-slot:body-content>
				<p class="text-base">
					Tất cả dữ liệu từ tổ chức của bạn sẽ bị mất. Bạn có chắc chắn muốn đặt
					lại database không?
				</p>
				<p class="mt-4 text-base">
					Vui lòng nhập
					<span class="font-semibold">{{ site.name }}</span> để xác nhận.
				</p>
				<FormControl class="mt-4 w-full" v-model="confirmSiteName" />
				<ErrorMessage class="mt-2" :message="$resources.resetDatabase.error" />
			</template>
		</Dialog>
	</Card>
</template>

<script>
import FileUploader from '@/components/FileUploader.vue';
import BackupFilesUploader from '@/components/BackupFilesUploader.vue';
import DatabaseAccessDialog from './DatabaseAccessDialog.vue';

export default {
	name: 'SiteDatabase',
	components: {
		FileUploader,
		BackupFilesUploader,
		DatabaseAccessDialog
	},
	props: ['site'],
	data() {
		return {
			confirmSiteName: '',
			showResetDialog: false,
			showMigrateDialog: false,
			showRestoreDialog: false,
			showDatabaseAccessDialog: false,
			selectedFiles: {
				database: null,
				public: null,
				private: null
			},
			wantToSkipFailingPatches: false
		};
	},
	resources: {
		restoreBackup() {
			return {
				url: 'press.api.site.restore',
				params: {
					name: this.site?.name,
					files: this.selectedFiles,
					skip_failing_patches: this.wantToSkipFailingPatches
				},
				validate() {
					if (!this.filesUploaded) {
						return 'Vui lòng tải lên database, public và private files để khôi phục.';
					}
				},
				onSuccess(jobName) {
					this.selectedFiles = {};
					this.$router.push({ name: 'SiteJobs', params: { jobName } });
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		},
		resetDatabase() {
			return {
				url: 'press.api.site.reinstall',
				params: {
					name: this.site?.name
				},
				validate() {
					if (this.confirmSiteName !== this.site?.name) {
						return 'Vui lòng nhập tên tổ chức để xác nhận.';
					}
				},
				onSuccess(jobName) {
					this.$router.push({ name: 'SiteJobs', params: { jobName } });
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		},
		migrateDatabase() {
			return {
				url: 'press.api.site.migrate',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					this.$router.push({
						name: 'SiteOverview',
						params: { site: this.site?.name }
					});
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		},
		clearCache() {
			return {
				url: 'press.api.site.clear_cache',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					this.$router.push({
						name: 'SiteOverview',
						params: { site: this.site?.name }
					});
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		}
	},
	methods: {
		migrateDatabase() {
			this.$resources.migrateDatabase.submit({
				name: this.site.name,
				skip_failing_patches: this.wantToSkipFailingPatches
			});
		},
		confirmClearCache() {
			this.$confirm({
				title: 'Xóa Cache',
				message: `
				<b>bench clear-cache</b> và <b>bench clear-website-cache</b> sẽ được thực hiện trên tổ chức của bạn. Bạn có chắc chắn muốn chạy các lệnh này không?
				`,
				actionLabel: 'Xóa Cache',
				actionColor: 'red',
				action: closeDialog => {
					this.$resources.clearCache.submit();
					closeDialog();
				}
			});
		}
	},
	computed: {
		permissions() {
			return {
				migrate: this.$account.hasPermission(
					this.site.name,
					'press.api.site.migrate'
				),
				restore: this.$account.hasPermission(
					this.site.name,
					'press.api.site.restore'
				),
				reset: this.$account.hasPermission(
					this.site.name,
					'press.api.site.reset'
				),
				access: this.$account.hasPermission(
					this.site.name,
					'press.api.site.enable_database_access'
				)
			};
		},
		filesUploaded() {
			return this.selectedFiles.database;
		}
	}
};
</script>
