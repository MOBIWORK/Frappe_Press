<template>
	<Card title="Hồ sơ">
		<div class="flex items-center border-b pb-3">
			<div class="relative">
				<Avatar
					size="2xl"
					:label="$account.user.first_name"
					:image="$account.user.user_image"
				/>
				<FileUploader
					@success="onProfilePhotoChange"
					fileTypes="image/*"
					:upload-args="{
						doctype: 'User',
						docname: $account.user.name,
						method: 'press.api.account.update_profile_picture'
					}"
				>
					<template v-slot="{ openFileSelector, uploading, progress, error }">
						<div class="ml-4">
							<button
								@click="openFileSelector()"
								class="absolute inset-0 grid w-full place-items-center rounded-full bg-black text-xs font-medium text-white opacity-0 transition hover:opacity-50 focus:opacity-50 focus:outline-none"
								:class="{ 'opacity-50': uploading }"
							>
								<span v-if="uploading">{{ progress }}%</span>
								<span v-else>Sửa</span>
							</button>
						</div>
					</template>
				</FileUploader>
			</div>
			<div class="ml-4">
				<h3 class="text-base font-semibold">
					{{ $account.user.first_name }} {{ $account.user.last_name }}
				</h3>
				<p class="mt-1 text-base text-gray-600">{{ $account.user.email }}</p>
			</div>
			<div class="ml-auto">
				<Button icon-left="edit" @click="showProfileEditDialog = true">
					Chỉnh sửa
				</Button>
			</div>
		</div>
		<div>
			<ListItem
				title="Trở thành nhà phát triển Marketplace"
				subtitle="Trở thành nhà xuất bản ứng dụng trên marketplace"
				v-if="showBecomePublisherButton"
			>
				<template #actions>
					<Button @click="confirmPublisherAccount()">
						<span>Trở thành nhà xuất bản</span>
					</Button>
				</template>
			</ListItem>
			<ListItem
				:title="teamEnabled ? 'Vô hiệu hóa tài khoản' : 'Kích hoạt tài khoản'"
				:subtitle="
					teamEnabled
						? 'Vô hiệu hóa tài khoản của bạn và dừng việc lập hóa đơn'
						: 'kích hoạt tài khoản của bạn và tiếp tục việc lập hóa đơn'
				"
			>
				<template #actions>
					<Button
						@click="
							() => {
								if (teamEnabled) {
									showDisableAccountDialog = true;
								} else {
									showEnableAccountDialog = true;
								}
							}
						"
					>
						<span :class="{ 'text-red-600': teamEnabled }">{{
							teamEnabled ? 'Vô hiệu hóa' : 'Kích hoạt'
						}}</span>
					</Button>
				</template>
			</ListItem>
		</div>
		<Dialog
			:options="{
				title: 'Cập nhật thông tin hồ sơ',
				actions: [
					{
						variant: 'solid',
						label: 'Lưu thay đổi',
						onClick: () => $resources.updateProfile.submit()
					}
				]
			}"
			v-model="showProfileEditDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl label="Họ" v-model="$account.user.last_name" />
					<FormControl label="Tên" v-model="$account.user.first_name" />
				</div>
				<ErrorMessage class="mt-4" :message="$resources.updateProfile.error" />
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: 'Vô hiệu hóa tài khoản',
				actions: [
					{
						label: 'Vô hiệu hóa',
						variant: 'solid',
						theme: 'red',
						loading: $resources.disableAccount.loading,
						onClick: () => $resources.disableAccount.submit()
					}
				]
			}"
			v-model="showDisableAccountDialog"
		>
			<template v-slot:body-content>
				<div class="prose text-base">
					Bằng cách xác nhận hành động này:
					<ul>
						<li>Tài khoản của bạn sẽ bị vô hiệu hóa</li>
						<li>
							Các tổ chức đang hoạt động của bạn sẽ bị đình chỉ ngay lập tức và
							sẽ bị xóa sau một tuần.
						</li>
						<li>Việc thanh toán tài khoản của bạn sẽ bị ngừng</li>
					</ul>
					Bạn có thể kích hoạt tài khoản của mình sau này bất cứ lúc nào. Bạn có
					muốn tiếp tục?
				</div>
				<ErrorMessage class="mt-2" :message="$resources.disableAccount.error" />
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: 'Kích hoạt tài khoản',
				actions: [
					{
						label: 'Kích hoạt',
						variant: 'solid',
						loading: $resources.enableAccount.loading,
						onClick: () => $resources.enableAccount.submit()
					}
				]
			}"
			v-model="showEnableAccountDialog"
		>
			<template v-slot:body-content>
				<div class="prose text-base">
					Xác nhận hành động này:
					<ul>
						<li>Tài khoản của bạn sẽ được kích hoạt</li>
						<li>Các tổ chức bị đình chỉ của bạn sẽ hoạt động</li>
						<li>Việc lập hóa đơn cho tài khoản của bạn sẽ được tiếp tục</li>
					</ul>
					Bạn có muốn tiếp tục không?
				</div>
				<ErrorMessage class="mt-2" :message="$resources.enableAccount.error" />
			</template>
		</Dialog>
	</Card>
	<FinalizeInvoicesDialog v-model="showFinalizeInvoicesDialog" />
</template>
<script>
import FileUploader from '@/components/FileUploader.vue';
import FinalizeInvoicesDialog from '../billing/FinalizeInvoicesDialog.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AccountProfile',
	components: {
		FileUploader,
		FinalizeInvoicesDialog
	},
	data() {
		return {
			showProfileEditDialog: false,
			showEnableAccountDialog: false,
			showDisableAccountDialog: false,
			showBecomePublisherButton: false,
			showFinalizeInvoicesDialog: false
		};
	},
	computed: {
		teamEnabled() {
			return $account.team.enabled;
		}
	},
	resources: {
		updateProfile() {
			let { first_name, last_name, email } = this.$account.user;
			return {
				url: 'press.api.account.update_profile',
				params: {
					first_name,
					last_name,
					email
				},
				onSuccess() {
					this.showProfileEditDialog = false;
					this.notifySuccess();
				}
			};
		},
		disableAccount: {
			url: 'press.api.account.disable_account',
			onSuccess(data) {
				this.showDisableAccountDialog = false;

				if (data === 'Unpaid Invoices') {
					this.showFinalizeInvoicesDialog = true;
				} else {
					notify({
						title: 'Tài khoản đã bị vô hiệu hóa',
						message: 'Tài khoản của bạn đã được vô hiệu hóa thành công',
						icon: 'check',
						color: 'green'
					});
					this.$account.fetchAccount();
				}
			}
		},
		enableAccount: {
			url: 'press.api.account.enable_account',
			onSuccess() {
				notify({
					title: 'Tài khoản đã được kích hoạt',
					message: 'Tài khoản của bạn đã được kích hoạt thành công',
					icon: 'check',
					color: 'green'
				});
				this.$account.fetchAccount();
				this.showEnableAccountDialog = false;
			}
		},
		isDeveloperAccountAllowed() {
			return {
				url: 'press.api.marketplace.developer_toggle_allowed',
				auto: true,
				onSuccess(data) {
					if (data) {
						this.showBecomePublisherButton = true;
					}
				}
			};
		},
		becomePublisher() {
			return {
				url: 'press.api.marketplace.become_publisher',
				onSuccess() {
					this.$router.push('/marketplace');
				}
			};
		}
	},
	methods: {
		onProfilePhotoChange() {
			this.$account.fetchAccount();
			this.notifySuccess();
		},
		notifySuccess() {
			notify({
				title: 'Thông tin hồ sơ đã được cập nhật',
				icon: 'check',
				color: 'green'
			});
		},
		confirmPublisherAccount() {
			this.$confirm({
				title: 'Trở thành nhà phát triển ứng dụng marketplace?',
				message:
					'Sau khi xác nhận, bạn sẽ có thể xuất bản ứng dụng lên Marketplace của chúng tôi.',
				actionLabel: 'Có',
				action: closeDialog => {
					this.$resources.becomePublisher.submit();
					closeDialog();
				}
			});
		}
	}
};
</script>
