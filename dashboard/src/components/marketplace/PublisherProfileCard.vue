<template>
	<div>
		<Card
			v-if="profileData && profileData.profile_created"
			title="Hồ sơ nhà xuất bản"
			subtitle="Hiển thị trên trang web marketplace"
		>
			<div class="divide-y-2">
				<ListItem
					title="Tên hiển thị"
					:description="displayName || 'Chưa đặt'"
				/>
				<ListItem
					title="Email liên hệ"
					:description="contactEmail || 'Chưa đặt'"
				/>
				<ListItem title="Website" :description="website || 'Chưa đặt'" />
			</div>

			<template #actions>
				<Button icon-left="edit" @click="showEditProfileDialog = true"
					>Chỉnh sửa</Button
				>
			</template>
		</Card>

		<Dialog
			:options="{
				title: 'Chỉnh sửa hồ sơ nhà xuất bản',
				actions: [
					{
						variant: 'solid',
						label: 'Lưu thay đổi',
						loading: $resources.updatePublisherProfile.loading,
						onClick: () => $resources.updatePublisherProfile.submit()
					}
				]
			}"
			v-model="showEditProfileDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl label="Tên hiển thị" v-model="displayName" />
					<FormControl
						label="Email liên hệ"
						type="email"
						v-model="contactEmail"
					/>
					<FormControl label="Website" v-model="website" />
				</div>

				<ErrorMessage
					class="mt-4"
					:message="$resources.updatePublisherProfile.error"
				/>
			</template>
		</Dialog>
	</div>
</template>

<script>
export default {
	props: ['profileData', 'showEditDialog'],
	emits: ['profileUpdated'],
	data() {
		return {
			showEditProfileDialog: false,
			displayName: '',
			contactEmail: '',
			website: ''
		};
	},
	resources: {
		updatePublisherProfile() {
			return {
				url: 'press.api.marketplace.update_publisher_profile',
				params: {
					profile_data: {
						display_name: this.displayName,
						contact_email: this.contactEmail,
						website: this.website
					}
				},
				validate() {
					if (!this.displayName) {
						return 'Yêu cầu có tên hiển thị.';
					}
				},
				onSuccess() {
					this.showEditProfileDialog = false;
					this.$emit('profileUpdated');
				}
			};
		}
	},
	watch: {
		profileData(data) {
			if (data && data.profile_created) {
				this.displayName = data.profile_info.display_name;
				this.contactEmail = data.profile_info.contact_email;
				this.website = data.profile_info.website;
			}
		},
		showEditDialog(value) {
			if (value) {
				this.showEditProfileDialog = true;
			}
		}
	}
};
</script>
