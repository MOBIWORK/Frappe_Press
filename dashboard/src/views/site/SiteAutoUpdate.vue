<template>
	<div>
		<div v-if="!$resources.getSiteAutoUpdateInfo.loading && !autoUpdateEnabled">
			<Alert :title="$t('SiteAutoUpdate_content_1')">
				<template #actions>
					<Button
						variant="solid"
						@click="enableAutoUpdate"
						:loading="$resources.enableAutoUpdate.loading"
						:loadingText="$t('Enabling')"
						>{{ $t('Enable') }}</Button
					>
				</template>
			</Alert>
		</div>
		<div v-else class="md:grid md:grid-cols-2">
			<Card :title="$t('Auto_Update')">
				<template
					#actions
					v-if="!$resources.getSiteAutoUpdateInfo.loading && autoUpdateEnabled"
				>
					<!-- Disable Button -->
					<Button
						@click="disableAutoUpdate"
						:loading="$resources.disableAutoUpdate.loading"
						:loadingText="$t('Disabling')"
						>{{ $t('Disable_Auto_Updates') }}</Button
					>
					<Button icon-left="edit" @click="showEditDialog = true">{{
						$t('Edit')
					}}</Button>
				</template>

				<div
					class="divide-y-2"
					v-if="!$resources.getSiteAutoUpdateInfo.loading && autoUpdateEnabled"
				>
					<ListItem
						:title="$t('Update_cycle')"
						:description="
							siteAutoUpdateInfo.update_trigger_frequency || $t('not_set')
						"
					/>

					<!-- For weekly updates only -->
					<ListItem
						v-if="siteAutoUpdateInfo.update_trigger_frequency === 'Weekly'"
						:title="$t('SiteAutoUpdate_content_2')"
						:description="siteAutoUpdateInfo.update_on_weekday"
					/>

					<ListItem
						:title="$t('SiteAutoUpdate_content_3')"
						:description="
							getFormattedTime(siteAutoUpdateInfo.update_trigger_time) ||
							$t('not_set')
						"
					/>

					<!-- Day of month description -->
					<div v-if="siteAutoUpdateInfo.update_trigger_frequency === 'Monthly'">
						<ListItem
							v-if="!siteAutoUpdateInfo.update_end_of_month"
							:title="$t('SiteAutoUpdate_content_4')"
							:description="
								siteAutoUpdateInfo.update_on_day_of_month.toString()
							"
						/>
						<ListItem
							v-else
							:title="$t('SiteAutoUpdate_content_4')"
							:description="$t('SiteAutoUpdate_content_5')"
						/>
					</div>

					<!-- Last triggered At -->
					<ListItem
						v-if="siteAutoUpdateInfo.auto_update_last_triggered_on"
						:title="$t('SiteAutoUpdate_content_6')"
						:description="siteAutoUpdateInfo.auto_update_last_triggered_on"
					/>
					<ListItem
						v-else
						:title="$t('SiteAutoUpdate_content_6')"
						:description="$t('SiteAutoUpdate_content_7')"
					/>
				</div>

				<!-- If updates are not enabled, show button -->
				<div
					class="py-10 text-center"
					v-if="!$resources.getSiteAutoUpdateInfo.loading && !autoUpdateEnabled"
				>
					<h3 class="text-sm text-gray-800">
						{{ $t('SiteAutoUpdate_content_8') }}
					</h3>
					<Button
						class="mt-3"
						variant="solid"
						@click="enableAutoUpdate"
						:loading="this.$resources.enableAutoUpdate.loading"
						loadingText="Enabling"
						>{{ $t('SiteAutoUpdate_content_9') }}</Button
					>
				</div>

				<!-- Loading Spinner button -->
				<div
					v-if="$resources.getSiteAutoUpdateInfo.loading"
					class="py-10 text-center"
				>
					<Button :loading="true">{{ $t('Loading') }}</Button>
				</div>

				<Dialog
					:options="{
						title: $t('SiteAutoUpdate_content_10'),
						actions: [
							{
								label: $t('save_changes'),
								variant: 'solid',
								loading: $resources.updateAutoUpdateInfo.loading,
								onClick: () => $resources.updateAutoUpdateInfo.submit()
							}
						]
					}"
					v-model="showEditDialog"
				>
					<!-- Edit From -->
					<template v-slot:body-content>
						<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
							<FormControl
								type="select"
								:label="$t('SiteAutoUpdate_content_11')"
								:options="frequencyOptions"
								v-model="updateFrequency"
							/>

							<FormControl
								type="select"
								:options="timeOptions"
								:label="$t('SiteAutoUpdate_content_3')"
								v-model="updateTime"
							/>

							<FormControl
								v-if="updateFrequency === 'Weekly'"
								type="select"
								:label="$t('SiteAutoUpdate_content_12')"
								:options="weekDayOptions"
								v-model="weekDay"
							/>

							<FormControl
								v-if="updateFrequency === 'Monthly'"
								type="select"
								:options="monthDayOptions"
								:label="$t('SiteAutoUpdate_content_13')"
								v-model.number="monthDay"
							/>
							<FormControl
								v-if="updateFrequency === 'Monthly'"
								type="checkbox"
								:label="$t('SiteAutoUpdate_content_14')"
								:checked="endOfMonth"
								v-model="endOfMonth"
							/>
						</div>
						<ErrorMessage
							class="mt-4"
							:message="$resources.disableAutoUpdate.error"
						/>

						<ErrorMessage
							class="mt-4"
							:message="$resources.updateAutoUpdateInfo.error"
						/>
					</template>
				</Dialog>

				<h4 class="mt-2 text-base text-gray-600">
					<strong>{{ $t('Note') }}:</strong>
					{{ $t('SiteAutoUpdate_content_15') }}
				</h4>

				<ErrorMessage
					class="mt-4"
					:message="$resources.enableAutoUpdate.error"
				/>
			</Card>
		</div>
	</div>
</template>

<script>
export default {
	name: 'SiteAutoUpdate',
	props: ['site'],
	data() {
		return {
			autoUpdateEnabled: null,
			lastTriggeredAt: null,
			updateFrequency: '',
			weekDay: '',
			monthDay: '',
			endOfMonth: false,
			updateTime: '',
			showEditDialog: false
		};
	},
	resources: {
		getSiteAutoUpdateInfo() {
			return {
				url: 'press.api.site.get_auto_update_info',
				params: {
					name: this.site?.name
				},
				auto: true,
				onSuccess(data) {
					this.autoUpdateEnabled = data.auto_updates_scheduled;
					this.updateFrequency = data.update_trigger_frequency;
					this.weekDay = data.update_on_weekday;
					this.endOfMonth = data.update_end_of_month;
					this.monthDay = data.update_on_day_of_month;
					this.lastTriggeredAt = data.auto_update_last_triggered_on;
					this.updateTime = this.getFormattedTime(data.update_trigger_time);
				}
			};
		},
		enableAutoUpdate() {
			return {
				url: 'press.api.site.enable_auto_update',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					this.$resources.getSiteAutoUpdateInfo.fetch();
				}
			};
		},
		disableAutoUpdate() {
			return {
				url: 'press.api.site.disable_auto_update',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					this.showEditDialog = false;
					this.$resources.getSiteAutoUpdateInfo.fetch();
				}
			};
		},
		updateAutoUpdateInfo() {
			return {
				url: 'press.api.site.update_auto_update_info',
				params: {
					name: this.site?.name,
					info: {
						auto_updates_scheduled: this.autoUpdateEnabled,
						update_trigger_frequency: this.updateFrequency,
						update_on_weekday: this.weekDay,
						update_end_of_month: this.endOfMonth,
						update_on_day_of_month: this.monthDay,
						auto_update_last_triggered_on: this.lastTriggeredAt,
						update_trigger_time: this.updateTime
					}
				},
				onSuccess() {
					this.showEditDialog = false;
					this.$resources.getSiteAutoUpdateInfo.fetch();
				}
			};
		}
	},
	methods: {
		enableAutoUpdate() {
			this.$resources.enableAutoUpdate.submit();
		},
		disableAutoUpdate() {
			this.$resources.disableAutoUpdate.submit();
		},
		getFormattedTime(timeStringFromServer) {
			if (!timeStringFromServer) {
				return;
			}
			// E.g. "8:19:00" --> "08:19"
			let timeParts = timeStringFromServer.split(':').slice(0, 2);
			return timeParts[0].padStart(2, '0') + ':' + timeParts[1];
		}
	},
	computed: {
		siteAutoUpdateInfo() {
			if (
				!this.$resources.getSiteAutoUpdateInfo.loading &&
				this.$resources.getSiteAutoUpdateInfo.data
			) {
				return this.$resources.getSiteAutoUpdateInfo.data;
			}
		},
		frequencyOptions() {
			return ['Daily', 'Weekly', 'Monthly'];
		},
		weekDayOptions() {
			return [
				{
					label: this.$t('Sunday'),
					value: 'Sunday'
				},
				{
					label: this.$t('Monday'),
					value: 'Monday'
				},
				{
					label: this.$t('Tuesday'),
					value: 'Tuesday'
				},
				{
					label: this.$t('Wednesday'),
					value: 'Wednesday'
				},
				{
					label: this.$t('Thursday'),
					value: 'Thursday'
				},
				{
					label: this.$t('Friday'),
					value: 'Friday'
				},
				{
					label: this.$t('Saturday'),
					value: 'Saturday'
				}
			];
		},
		monthDayOptions() {
			let ops = [];
			for (let i = 1; i < 31; ++i) {
				ops.push(i.toString());
			}
			return ops;
		},
		timeOptions() {
			let ops = [];
			for (let i = 0; i < 24; i++) {
				const currentHour = String(i).padStart(2, '0');
				ops.push(`${currentHour}:00`);
				ops.push(`${currentHour}:30`);
			}
			return ops;
		}
	}
};
</script>
