import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AuditorComponent } from './auditor';

describe('Auditor', () => {
  let component: AuditorComponent;
  let fixture: ComponentFixture<AuditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AuditorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
