<template>
	<Card :title="$t('profile')">
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
								<span v-else>{{ $t('edit') }}</span>
							</button>
						</div>
					</template>
				</FileUploader>
			</div>
			<div class="ml-4">
				<h3 class="text-base font-semibold">
					{{ $account.user.first_name }}
				</h3>
				<p class="mt-1 text-base text-gray-600">{{ $account.user.email }}</p>
			</div>
			<div class="ml-auto">
				<Button icon-left="edit" @click="showProfileEditDialog = true">
					{{ $t('edit') }}
				</Button>
			</div>
		</div>
		<div>
			<ListItem
				:title="$t('accountprofile_content_1')"
				:subtitle="$t('accountprofile_content_2')"
				v-if="showBecomePublisherButton"
			>
				<template #actions>
					<Button @click="confirmPublisherAccount()">
						<span>{{ $t('become_a_publisher') }}</span>
					</Button>
				</template>
			</ListItem>
			<ListItem
				:title="teamEnabled ? $t('disable_account') : $t('enable_account')"
				:subtitle="
					teamEnabled
						? $t('accountprofile_content_3')
						: $t('accountprofile_content_4')
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
							teamEnabled ? $t('disable') : $t('enable')
						}}</span>
					</Button>
				</template>
			</ListItem>
		</div>
		<Dialog
			:options="{
				title: $t('update_profile_information'),
				actions: [
					{
						variant: 'solid',
						label: $t('save_changes'),
						onClick: () => $resources.updateProfile.submit()
					}
				]
			}"
			v-model="showProfileEditDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4">
					<FormControl
						:label="$t('full_name')"
						v-model="$account.user.first_name"
					/>
				</div>
				<ErrorMessage class="mt-4" :message="$resources.updateProfile.error" />
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: $t('disable_account'),
				actions: [
					{
						label: $t('disable'),
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
					{{ $t('accountprofile_content_5') }}
					<ul>
						<li>{{ $t('accountprofile_content_6') }}</li>
						<li>
							{{ $t('accountprofile_content_7') }}
						</li>
						<li>{{ $t('accountprofile_content_8') }}</li>
					</ul>
					{{ $t('accountprofile_content_9') }}
				</div>
				<ErrorMessage class="mt-2" :message="$resources.disableAccount.error" />
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: $t('enable_account'),
				actions: [
					{
						label: $t('enable'),
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
					{{ $t('accountprofile_content_10') }}
					<ul>
						<li>{{ $t('accountprofile_content_11') }}</li>
						<li>{{ $t('accountprofile_content_12') }}</li>
						<li>{{ $t('accountprofile_content_13') }}</li>
					</ul>
					{{ $t('accountprofile_content_14') }}
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
			let { first_name, email } = this.$account.user;
			return {
				url: 'press.api.account.update_profile',
				params: {
					first_name,
					email
				},
				onSuccess() {
					this.showProfileEditDialog = false;
					this.notifySuccess();
				}
			};
		},
		disableAccount() {
			return {
				url: 'press.api.account.disable_account',
				params: {
					lang: this?.$i18n.locale
				},
				onSuccess(data) {
					this.showDisableAccountDialog = false;

					if (data === 'Unpaid Invoices') {
						this.showFinalizeInvoicesDialog = true;
					} else {
						notify({
							title: this.$t('account_disabled'),
							message: this.$t('accountprofile_content_15'),
							icon: 'check',
							color: 'green'
						});
						this.$account.fetchAccount();
					}
				}
			};
		},
		enableAccount() {
			return {
				url: 'press.api.account.enable_account',
				params: {
					lang: this.$i18n.locale
				},
				onSuccess() {
					notify({
						title: this.$t('account_enabled'),
						message: this.$t('accountprofile_content_16'),
						icon: 'check',
						color: 'green'
					});
					this.$account.fetchAccount();
					this.showEnableAccountDialog = false;
				}
			};
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
				title: this.$t('Updated_profile_information'),
				icon: 'check',
				color: 'green'
			});
		},
		confirmPublisherAccount() {
			this.$confirm({
				title: this.$t('accountprofile_content_17'),
				message: this.$t('accountprofile_content_18'),
				actionLabel: this.$t('yes'),
				action: closeDialog => {
					this.$resources.becomePublisher.submit();
					closeDialog();
				}
			});
		}
	}
};
</script>
