<template>
	<div>
		<Card
			v-if="profileData && profileData.profile_created"
			:title="$t('Publisher_Profile')"
			:subtitle="$t('PublisherProfileCard_content_1')"
		>
			<div class="divide-y-2">
				<ListItem
					:title="$t('Display_Name')"
					:description="displayName || $t('not_set')"
				/>
				<ListItem
					:title="$t('Contact_Email')"
					:description="contactEmail || $t('not_set')"
				/>
				<ListItem title="Website" :description="website || $t('not_set')" />
			</div>

			<template #actions>
				<Button icon-left="edit" @click="showEditProfileDialog = true">{{
					$t('Edit')
				}}</Button>
			</template>
		</Card>

		<Dialog
			:options="{
				title: $t('PublisherProfileCard_content_2'),
				actions: [
					{
						variant: 'solid',
						label: $t('save_changes'),
						loading: $resources.updatePublisherProfile.loading,
						onClick: () => $resources.updatePublisherProfile.submit()
					}
				]
			}"
			v-model="showEditProfileDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl :label="$t('Display_Name')" v-model="displayName" />
					<FormControl
						:label="$t('Contact_Email')"
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
	emits: ['profileUpdated', 'update:showEditDialog'],
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
						return this.$t('PublisherProfileCard_content_3');
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
		showEditProfileDialog(value) {
			if (!value) {
				this.$emit('update:showEditDialog', false);
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
